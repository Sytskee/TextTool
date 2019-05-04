import sys
from datetime import datetime
from io import StringIO
from json import load, dumps
from multiprocessing import Process
from os import path, listdir

from tornado.websocket import WebSocketHandler

from classifier.TextClassifier import TextClassifier
from classifier.TextClassifier import pipeline_and_parameters2 as pipeline_and_parameters


class SettingsWebSocket(WebSocketHandler):
    __clients__ = []

    def initialize(self, webapp_settings, status_report_queue):
        self.webapp_settings = webapp_settings
        self.status_report_queue = status_report_queue

    def open(self):
        SettingsWebSocket.__clients__.append(self)
        self.write_message(dumps(self.webapp_settings))

    def on_message(self, message):
        message_io = StringIO(message)
        changed_setting = load(message_io)

        for key, value in changed_setting.items():
            if self.webapp_settings[key] != value:
                self.webapp_settings[key] = value

                if key == "classifier_running":
                    if value:
                        global text_classification_process
                        text_classification_process = Process(target=self.start_text_classifier)
                        text_classification_process.start()
                    else:
                        self.stop_text_classifier()
                elif key == "data_files_path":
                    if path.isdir(value):
                        dirs = [path.join(value, o) for o in
                                listdir(value) if
                                path.isdir(path.join(value, o))]
                        self.webapp_settings["number_of_classes"] = dirs.__len__()
                    else:
                        self.webapp_settings["number_of_classes"] = -1
                        self.status_report_queue.put("Not a valid directory selected")

        self.write_message(self.webapp_settings)

    def data_received(self, chunk):
        pass

    def on_close(self):
        SettingsWebSocket.__clients__.remove(self)

    @classmethod
    def write_settings_to_clients(cls):
        print("write_settings_to_clients: " + str(cls.__clients__.__len__()))
        for client in cls.__clients__:
            client.write_message(client.webapp_settings)

    def start_text_classifier(self):
        # Set variable to language of dataset, e.g. 'dutch', 'english' or any other language supported by NLTK
        language = 'dutch'
        error = None

        try:
            # Create the classifier with the language and dataset:
            text_classifier = TextClassifier(language, self.webapp_settings["data_files_path"],
                                             self.status_report_queue)
            number_of_groups = text_classifier.get_groups_counter()

            for i in range(number_of_groups):
                self.status_report_queue.put(
                    '{}: {} outer loops, start fitting {}'.format(datetime.now().strftime('%H:%M:%S'),
                                                                  number_of_groups, i + 1))

                text_classifier.set_next_group_data(i)

                # Different scoring metrics can be used:
                if self.webapp_settings["number_of_classes"] == 2:
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
                                            self.webapp_settings["data_files_path"])

                    fold_process = Process(target=text_classifier.train_and_predict)
                    fold_process.start()

                    while fold_process.is_alive():
                        fold_process.join(0.5)
                        sys.stdout.flush()
        except Exception as exception:
            print("Unexpected error:", sys.exc_info()[0])
            self.status_report_queue.put("Something went wrong: " + str(exception))
            error = exception

        # All done
        self.status_report_queue.put('{}: All done!'.format(datetime.now().strftime('%H:%M:%S')))
        self.stop_text_classifier()

        if error is not None:
            raise error

    def stop_text_classifier(self):
        global text_classification_process

        self.status_report_queue.put("Stop")

        if text_classification_process is not None:
            if text_classification_process.is_alive():
                text_classification_process.terminate()
                text_classification_process.join()

            text_classification_process = None

        self.webapp_settings["classifier_running"] = False
        SettingsWebSocket.write_settings_to_clients()
