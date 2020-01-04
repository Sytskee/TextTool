import sys

from datetime import datetime
from io import StringIO
from json import load, dumps
from multiprocessing import Process
from typing import Any

import tornado.web
from tornado import httputil

from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from classifier.TextClassifier import TextClassifier
from classifier.TextClassifier import pipeline_and_parameters2 as pipeline_and_parameters
from user_interface.handlers.SettingsHandler import SettingsHandler


def start_text_classifier(settings, status_report_queue):
    # Set variable to language of dataset, e.g. 'dutch', 'english' or any other language supported by NLTK
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

    if error is not None:
        raise error


class SettingsWebSocket(WebSocketHandler):
    def initialize(self, status_report_queue):
        self.status_report_queue = status_report_queue

        self.text_classification_process = None

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
        classifier_running_changed = False

        for group, value_dict in changed_setting.items():
            for key, value in value_dict.items():
                if settings[group][key] != value:
                    self.__app_settings_handler.set(group, key, value)

                    if key == "classifier_running":
                        classifier_running_changed = True

        # Get a fresh copy with all new values
        settings = self.__app_settings_handler.get_settings()

        self.__app_settings_handler.save_settings()
        self.write_message(settings)

        if classifier_running_changed:
            self.__classifier_running_changed(settings)

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

    def __classifier_running_changed(self, settings):
        if settings[SettingsHandler.PROGRAM_SETTINGS].get("classifier_running"):
            self.text_classification_process = Process(
                target=start_text_classifier,
                args=(settings, self.status_report_queue,),
                name="Text-Classifier")
            self.text_classification_process.start()
        else:
            self.status_report_queue.put("Stop")

            if self.text_classification_process is not None:
                if self.text_classification_process.is_alive():
                    self.text_classification_process.terminate()
                    self.text_classification_process.join(timeout=1)

                self.text_classification_process = None