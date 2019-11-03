from util.Singleton import Singleton


class AppSettingsHandler(metaclass=Singleton):
    def __init__(self, output_path):
        self.__settings = {
            "software_version": "0.2",
            "number_of_classes": -1,
            "classifier_running": False,
            "data_files_path": r"C:\Users\Joost\Desktop\JoostTest",
            "n_splits": 3,
            "output_path": output_path
        }

        self.__onchange_listeners = list()

    def get_app_settings(self):
        """Get a copy of the current settings. Be aware that this is a copy, changes to the returned dictionary do not
            reflect in the settings

            Returns:
                A copy of the current settings dictionary"""
        settings_copy = self.__settings.copy()
        settings_copy.pop('io_loops', None)
        return settings_copy

    def set(self, key, new_value):
        old_value = self.__settings.get(key)
        self.__settings[key] = new_value

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
