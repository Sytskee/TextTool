from pathlib import Path
from util.Singleton import Singleton
from nltk.corpus import stopwords


class AppSettingsHandler(metaclass=Singleton):
    def __init__(self, current_path, status_report_queue):
        output_path = os.path.join(current_path, 'output', '')

        self.__status_report_queue = status_report_queue
        self.__settings = dict()
        self.__onchange_listeners = list()

        self.set("software_version", "0.2")
        self.set("number_of_classes", -1)
        self.set("n_splits", 3)
        self.set("n_splits_min", 3)
        self.set("n_splits_max", 10)
        self.set("classifier_running", False)
        self.set("output_path", output_path)
        self.set("language_options", stopwords.fileids())
        self.set("language", "english")

        self.set("data_files_path", r"C:\Users\Joost\Desktop\JoostTest")

    def get_app_settings(self):
        """Get a copy of the current settings. Be aware that this is a copy, changes to the returned dictionary do not
            reflect in the settings

            Returns:
                A copy of the current settings dictionary"""
        settings_copy = self.__settings.copy()
        settings_copy.pop('io_loops', None)
        return settings_copy

    def set(self, key, new_value):
        if new_value != self.__settings.get(key):
            old_value = self.__settings.get(key)
            self.__settings[key] = new_value

            self.__handle_special_cases(key, new_value)
            self.__notify(key, old_value, new_value)

    def get(self, key):
        return self.__settings.get(key)

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
                self.__status_report_queue.put("Not a valid directory selected")
