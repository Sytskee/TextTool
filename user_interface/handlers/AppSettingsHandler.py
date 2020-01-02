from pathlib import Path
from util.Singleton import Singleton
from nltk.corpus import stopwords


class AppSettingsHandler(metaclass=Singleton):
    APP_SETTINGS = "app_settings"

    def __init__(self, current_path, status_report_queue, config):
        self.__status_report_queue = status_report_queue
        self.__config = config
        self.__onchange_listeners = list()
        self.__set_configuration_defaults(current_path)

    def get_app_settings(self):
        """Get a copy of the current settings. Be aware that this is a copy, changes to the returned dictionary do not
            reflect in the settings

            Returns:
                A copy of the current settings dictionary"""
        settings_copy = self.__config[self.APP_SETTINGS].copy()
        settings_copy.pop('io_loops', None)
        return settings_copy

    def set(self, key, new_value):
        if new_value != self.__config['app_settings'].get(key):
            old_value = self.__config['app_settings'].get(key)
            self.__config['app_settings'][key] = new_value

            self.__handle_special_cases(key, new_value)
            self.__notify(key, old_value, new_value)

    def get(self, key):
        return self.__config['app_settings'].get(key)

    def register_onchange(self, listener):
        self.__onchange_listeners.append(listener)

    def unregister_onchange(self, listener):
        self.__onchange_listeners.remove(listener)

    def __notify(self, key, old_value, new_value):
        for listener in self.__onchange_listeners:
            listener(key, old_value, new_value)

    def __handle_special_cases(self, key, new_value):
        if key == "data_files_path":
            new_files_path = Path(new_value)

            if new_files_path.is_dir():
                dirs = [x for x in new_files_path.iterdir() if x.is_dir()]
                self.set("number_of_classes", dirs.__len__())
            else:
                self.set("number_of_classes", -1)
                self.__status_report_queue.put("Not a valid directory selected: " + new_value)

    def __set_configuration_defaults(self, current_path):
        self.__config.set(AppSettingsHandler.APP_SETTINGS, "number_of_classes", -1)
        self.__config.set(AppSettingsHandler.APP_SETTINGS, "n_splits", 3)
        self.__config.set(AppSettingsHandler.APP_SETTINGS, "n_splits_min", 3)
        self.__config.set(AppSettingsHandler.APP_SETTINGS, "n_splits_max", 10)
        self.__config.set(AppSettingsHandler.APP_SETTINGS, "classifier_running", False)
        self.__config.set(AppSettingsHandler.APP_SETTINGS, "output_path", current_path.joinpath("output"))
        self.__config.set(AppSettingsHandler.APP_SETTINGS, "language_options", stopwords.fileids())
        self.__config.set(AppSettingsHandler.APP_SETTINGS, "language", "english")
        self.__config.set(AppSettingsHandler.APP_SETTINGS, "data_files_path", current_path.joinpath("data"))
