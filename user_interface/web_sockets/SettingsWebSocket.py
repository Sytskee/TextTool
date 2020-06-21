import sys

from curses import ascii
from datetime import datetime
from io import StringIO
from json import load, dumps
from multiprocessing import Process

from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from executors.ApplyPickle import ApplyPickle
from executors.TextClassifier import TextClassifier
from executors.TextClassifier import pipeline_and_parameters2 as pipeline_and_parameters
from user_interface.handlers.SettingsHandler import SettingsHandler


def start_text_classifier(settings, status_report_queue):
    error = None

    try:
        # Create the classifier with the language and dataset:
        text_classifier = TextClassifier(
            settings[SettingsHandler.USER_SETTINGS]["language"],
            settings[SettingsHandler.USER_SETTINGS]["data_files_path"],
            settings[SettingsHandler.USER_SETTINGS]["n_splits"],
            settings[SettingsHandler.USER_SETTINGS]["output_path"],
            status_report_queue)

        number_of_groups = text_classifier.get_groups_counter()

        for i in range(number_of_groups):
            status_report_queue.put(
                '{}: {} outer loops, start fitting {}'.format(datetime.now().strftime('%H:%M:%S'),
                                                              number_of_groups, i + 1))

            text_classifier.set_next_group_data(i)

            # Different scoring metrics can be used:
            if settings[SettingsHandler.PROGRAM_SETTINGS]["number_of_classes"] == 2:
                # For binary classifiers: ['accuracy', 'precision', 'recall', 'f1']
                scorings = ['f1']
            else:
                # For multiclass classifiers: ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted'] or
                #                             ['accuracy', 'precision_micro', 'recall_micro', 'f1_micro'] or
                #                             ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
                scorings = ['f1_weighted']

            # Apply pipeline and parameters:
            for scoring in scorings:
                pipeline_and_parameters(
                    text_classifier,
                    scoring,
                    [result_scoring for result_scoring in scorings if result_scoring is not scoring])

                fold_process = Process(target=text_classifier.train_and_predict)
                fold_process.start()

                while fold_process.is_alive():
                    fold_process.join(0.5)
                    sys.stdout.flush()
    except Exception as exception:
        print("Unexpected error:", sys.exc_info()[0])
        status_report_queue.put("Something went wrong: " + str(exception))
        error = exception

    # All done
    status_report_queue.put('{}: All done!'.format(datetime.now().strftime('%H:%M:%S')))
    status_report_queue.put(
        str(ascii.BEL) + dumps({
            "group": SettingsHandler.PROGRAM_SETTINGS,
            "key": "apply_pickle_running",
            "value": False
        }))

    if error is not None:
        raise error


def start_applying_pickle(settings, status_report_queue):
    error = None

    try:
        apply_pickle = ApplyPickle(
            settings[SettingsHandler.USER_SETTINGS]["data_files_path_pickle"],
            settings[SettingsHandler.USER_SETTINGS]["pickle_file_path"],
            settings[SettingsHandler.USER_SETTINGS]["output_path"],
            status_report_queue)

        apply_pickle.predict()
    except Exception as exception:
        print("Unexpected error:", sys.exc_info()[0])
        status_report_queue.put("Something went wrong: " + str(exception))
        error = exception

    # All done
    status_report_queue.put('{}: All done!'.format(datetime.now().strftime('%H:%M:%S')))
    status_report_queue.put(
        str(ascii.BEL) + dumps({
            "group": SettingsHandler.PROGRAM_SETTINGS,
            "key": "apply_pickle_running",
            "value": False
        }))

    if error is not None:
        raise error


class SettingsWebSocket(WebSocketHandler):
    def initialize(self, status_report_queue):
        self.status_report_queue = status_report_queue

        self.executing_process = None

        self.__app_settings_handler = SettingsHandler()
        self.__app_settings_handler.register_onchange(self.setting_changed)
        self.__app_settings_handler.set(SettingsHandler.INTERNAL_SETTINGS, 'io_loops', dict())

    @staticmethod
    def setting_changed(key, old_value, new_value):
        SettingsWebSocket.write_settings_to_clients()

    def open(self):
        self.__app_settings_handler.get(SettingsHandler.INTERNAL_SETTINGS, "io_loops")[self] = IOLoop.current()
        self.write_message(dumps(self.__app_settings_handler.get_settings()))

    def on_message(self, message):
        message_io = StringIO(message)
        changed_setting = load(message_io)

        settings = self.__app_settings_handler.get_settings()
        application_running_changed = False

        for group, value_dict in changed_setting.items():
            for key, value in value_dict.items():
                if settings[group][key] != value:
                    self.__app_settings_handler.set(group, key, value)

                    if (group == SettingsHandler.PROGRAM_SETTINGS) and (key in settings[SettingsHandler.PROGRAM_SETTINGS]["executors"]):
                        application_running_changed = True

        self.__app_settings_handler.save_settings()

        # Get a fresh copy with all new values
        settings = self.__app_settings_handler.get_settings()
        self.write_message(settings)

        if application_running_changed:
            self.__application_running_changed(settings)

    def data_received(self, chunk):
        pass

    def on_close(self):
        self.__app_settings_handler.get(SettingsHandler.INTERNAL_SETTINGS, "io_loops").pop(self, None)

    @classmethod
    def write_settings_to_clients(cls):
        app_settings_handler = SettingsHandler()
        io_loops = app_settings_handler.get(SettingsHandler.INTERNAL_SETTINGS, "io_loops")

        print("write_settings_to_clients: " + str(io_loops.__len__()))
        for client, io_loop in io_loops.items():
            io_loop.add_callback(client.write_message, dumps(app_settings_handler.get_settings()))

    def __application_running_changed(self, settings):
        if settings[SettingsHandler.PROGRAM_SETTINGS].get("classifier_running"):
            self.executing_process = Process(
                target=start_text_classifier,
                args=(settings, self.status_report_queue,),
                name="Text-Classifier")
            self.executing_process.start()
        elif settings[SettingsHandler.PROGRAM_SETTINGS].get("apply_pickle_running"):
            self.executing_process = Process(
                target=start_applying_pickle,
                args=(settings, self.status_report_queue,),
                name="Apply-Pickle")
            self.executing_process.start()
        else:
            self.status_report_queue.put("Stop")

            if self.executing_process is not None:
                if self.executing_process.is_alive():
                    self.executing_process.terminate()
                    self.executing_process.join(timeout=1)

                self.executing_process = None
