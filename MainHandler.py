import concurrent.futures
import datetime
import json
import io
import multiprocessing
import os
import sys
import tornado.ioloop
import tornado.queues
import tornado.web
import tornado.websocket

# Fix for placing helper files in the same folder
PACKAGE_PARENT = '..'

if getattr(sys, 'frozen', False):
    # frozen
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    # unfrozen
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from TextClassifier import TextClassifier
from CustomTokenizer import CustomTokenizer
from SelectAtMostKBest import SelectAtMostKBest
from TextClassifier import pipeline_and_parameters2 as pipeline_and_parameters


webapp_path = os.path.join(os.path.dirname(__file__), "webapp")
status_report_queue = multiprocessing.Queue()
logging_web_socket = None
logging_queue = tornado.queues.Queue()
text_classification_process = None


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", webapp_settings=webapp_settings)


class LoggingWebSocket(tornado.websocket.WebSocketHandler):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    @tornado.concurrent.run_on_executor
    def get_logging(self):
        global status_report_queue
        self.write_message(status_report_queue.get() + "\r\n")
        tornado.ioloop.IOLoop.current().add_callback(self.get_logging)

    def initialize(self):
        tornado.ioloop.IOLoop.current().add_callback(self.get_logging)

    def on_message(self, message):
        self.write_message(u"You said: " + message + "\r\n")


class SettingsWebSocket(tornado.websocket.WebSocketHandler):
    clients = []

    def open(self):
        SettingsWebSocket.clients.append(self)
        self.write_message(json.dumps(webapp_settings))

    def on_message(self, message):
        global webapp_settings
        global status_report_queue
        message_io = io.StringIO(message)
        changed_setting = json.load(message_io)

        for key, value in changed_setting.items():
            if webapp_settings[key] != value:
                webapp_settings[key] = value

                if key == "classifier_running":
                    if value:
                        global text_classification_process
                        text_classification_process = multiprocessing.Process(target=start_text_classifier, args=(webapp_settings, status_report_queue))
                        text_classification_process.start()
                    else:
                        stop_text_classifier(webapp_settings)
                elif key == "data_files_path":
                    if os.path.isdir(value):
                        dirs = [os.path.join(value, o) for o in
                                os.listdir(value) if
                                os.path.isdir(os.path.join(value, o))]
                        webapp_settings["number_of_classes"] = dirs.__len__()
                    else:
                        webapp_settings["number_of_classes"] = -1
                        status_report_queue.put("Not a valid directory selected")

        self.write_message(webapp_settings)

    @classmethod
    def write_settings_to_clients(cls):
        print("write_settings_to_clients: " + str(cls.clients.__len__()))
        for client in cls.clients:
            client.write_message(webapp_settings)

    def on_close(self):
        SettingsWebSocket.clients.remove(self)

def start_text_classifier(webapp_settings, status_report_queue):
    # Set variable to language of dataset, e.g. 'dutch', 'english' or any other language supported by NLTK
    language = 'dutch'
    error = None

    try:
        # Create the classifier with the language and dataset:
        text_classifier = TextClassifier(language, webapp_settings["data_files_path"], status_report_queue)
        number_of_groups = text_classifier.get_groups_counter()

        for i in range(number_of_groups):
            status_report_queue.put('{}: {} outer loops, start fitting {}'.format(datetime.datetime.now().strftime('%H:%M:%S'), number_of_groups, i + 1))

            text_classifier.set_next_group_data(i)

            # Different scoring metrics can be used:
            if webapp_settings["number_of_classes"] == 2:
                # For binary classifiers: ['accuracy', 'precision', 'recall', 'f1']
                scorings = ['f1']
            else:
                # For multiclass classifiers: ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted'] or
                #                             ['accuracy', 'precision_micro', 'recall_micro', 'f1_micro'] or
                #                             ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
                scorings = ['f1_weighted']

            # Apply pipeline and parameters:
            for scoring in scorings:
                pipeline_and_parameters(text_classifier,
                                        scoring,
                                        [result_scoring for result_scoring in scorings if
                                         result_scoring is not scoring],
                                        text_classifier.development_filenames,
                                        webapp_settings["data_files_path"])

                fold_process = multiprocessing.Process(target=text_classifier.train_and_predict)
                fold_process.start()

                while fold_process.is_alive():
                    fold_process.join(0.5)
                    sys.stdout.flush()
    except Exception as exception:
        print("Unexpected error:", sys.exc_info()[0])
        status_report_queue.put("Something went wrong: " + str(exception))
        error = exception

    # All done
    status_report_queue.put('{}: All done!'.format(datetime.datetime.now().strftime('%H:%M:%S')))
    stop_text_classifier(webapp_settings)

    if error is not None:
        raise error


def stop_text_classifier(webapp_settings):
    global text_classification_process

    status_report_queue.put("Stop")

    if text_classification_process is not None:
        if text_classification_process.is_alive():
            text_classification_process.terminate()
            text_classification_process.join()

        text_classification_process = None

    webapp_settings["classifier_running"] = False
    SettingsWebSocket.write_settings_to_clients()


webapp_settings = {
    "software_version": "0.2",
    "data_files_path": r"C:\Users\Joost\Desktop\InterapyTest",
    "number_of_classes": -1,
    "classifier_running": False
}

settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "debug": True
}

application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/index", IndexHandler),
        (r"/api/v1/logging", LoggingWebSocket),
        (r"/api/v1/settings", SettingsWebSocket)
    ],
    **settings
)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    status_report_queue.close()
