import json

from pathlib import Path
from util.Singleton import Singleton
from nltk.corpus import stopwords
from sklearn.metrics import SCORERS


class SettingsHandler(metaclass=Singleton):
    USER_SETTINGS = "user"
    PROGRAM_SETTINGS = "program"
    CLASSIFIER_SETTINGS = "classifier"
    INTERNAL_SETTINGS = "internal"

    def __init__(self, current_path, status_report_queue, settings, settings_file):
        self.__status_report_queue = status_report_queue
        self.__settings = settings
        self.__settings_file = settings_file

        self.__onchange_listeners = list()
        self.__set_configuration_defaults(current_path)

    def get_settings(self):
        """Get a copy of the current settings. Be aware that this is a copy, changes to the returned dictionary do not
            reflect in the settings

            Returns:
                A copy of the current settings dictionary"""
        settings_copy = dict(self.__settings)
        settings_copy.pop(SettingsHandler.INTERNAL_SETTINGS, None)
        return settings_copy

    def set(self, group, key, new_value):
        old_value = self.__settings[group].get(key)

        if new_value != old_value:
            self.__settings[group][key] = new_value

            self.__handle_special_cases(key, new_value)
            self.__notify(key, old_value, new_value)

    def get(self, group, key):
        return self.__settings[group].get(key)

    def register_onchange(self, listener):
        self.__onchange_listeners.append(listener)

    def unregister_onchange(self, listener):
        self.__onchange_listeners.remove(listener)

    def save_settings(self):
        settings_copy = dict(self.__settings)
        settings_copy.pop(SettingsHandler.PROGRAM_SETTINGS, None)
        settings_copy.pop(SettingsHandler.INTERNAL_SETTINGS, None)

        with open(self.__settings_file, 'w') as configfile:
            json.dump(settings_copy, configfile, sort_keys=True, indent=2)

    def __notify(self, key, old_value, new_value):
        for listener in self.__onchange_listeners:
            listener(key, old_value, new_value)

    def __handle_special_cases(self, key, new_value):
        if key == "data_files_path":
            new_files_path = Path(new_value)

            if new_files_path.is_dir():
                dirs = [x for x in new_files_path.iterdir() if x.is_dir()]
                self.set(SettingsHandler.PROGRAM_SETTINGS, "number_of_classes", dirs.__len__())
            else:
                self.set(SettingsHandler.PROGRAM_SETTINGS, "number_of_classes", -1)
                self.__status_report_queue.put("Not a valid directory selected: " + new_value)
        elif key.startswith("chi2__k_"):
            start = self.get(SettingsHandler.CLASSIFIER_SETTINGS, "chi2__k_start")
            stop = self.get(SettingsHandler.CLASSIFIER_SETTINGS, "chi2__k_stop")
            step = self.get(SettingsHandler.CLASSIFIER_SETTINGS, "chi2__k_step")
            is_all_set = self.get(SettingsHandler.CLASSIFIER_SETTINGS, "chi2__k_all")

            chi2__k = self.create_chi2_k_value(start, stop, step, is_all_set)
            self.set(SettingsHandler.CLASSIFIER_SETTINGS, "chi2__k", chi2__k)
        elif key.startswith("helper_"):
            real_key = key[7:]

            if real_key == "text__vect__stop_words":
                result = []

                if True in new_value:
                    language = self.__settings[SettingsHandler.USER_SETTINGS]["language"]
                    result.append(stopwords.words(language))

                if False in new_value:
                    result.append(None)

                self.__settings[SettingsHandler.CLASSIFIER_SETTINGS][real_key] = result
            elif real_key == "clf__class_weight":
                result = []

                if True in new_value:
                    result.append("balanced")

                if False in new_value:
                    result.append(None)

                self.__settings[SettingsHandler.CLASSIFIER_SETTINGS][real_key] = result

    def __set_configuration_defaults(self, current_path):
        self.__settings[SettingsHandler.PROGRAM_SETTINGS] = {
            "software_version": "0.2",
            "number_of_classes": -1,
            "language_options": stopwords.fileids(),
            "classifier_running": False,
            "apply_pickle_running": False,
            "executors": ["classifier_running", "apply_pickle_running"],
            "text__vect__ngram_range_options": [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (1, 2), (1, 3), (1, 4), (1, 5)],
            "scoring_options": sorted(SCORERS.keys()),
        }

        self.__settings[SettingsHandler.USER_SETTINGS] = {
            "n_splits": 3,
            "n_splits_min": 2,
            "n_splits_max": 10,
            "output_path": str(current_path.joinpath("output")),
            "language": "english",
            "data_files_path": str(current_path.joinpath("data")),
            "data_files_path_pickle": str(current_path.joinpath("data")),
            "pickle_file_path": str(current_path.joinpath("output", "*.pkl")),
        }

        chi2__k_start = 10
        chi2__k_step = 20
        chi2__k_stop = 501
        chi2__k_all = True
        chi2__k = self.create_chi2_k_value(chi2__k_start, chi2__k_stop, chi2__k_step, chi2__k_all)

        self.__settings[SettingsHandler.CLASSIFIER_SETTINGS] = {
            "text__vect__min_df": [1, 2, 3],  # Number of training documents a term should occur in
            "text__vect__ngram_range": [(1, 1), (2, 2), (3, 3), (1, 3)],  # Test uni-, bi-, tri-, or N-multigrams ranging from 1-3
            "text__vect__stop_words": [None],
            "helper_text__vect__stop_words": [False],  # Do/do not remove stopwords
            "text__tfidf__use_idf": [True, False],  # Weight terms by tf or tfidf
            "chi2__k_start": chi2__k_start,
            "chi2__k_step": chi2__k_step,
            "chi2__k_stop": chi2__k_stop,
            "chi2__k_all": chi2__k_all,
            "chi2__k": chi2__k,  # Select K most informative features
            "clf__C": [1, 2, 3, 10, 100, 1000],  # Compare different values for C parameter
            "helper_clf__class_weight": [True, False],
            "clf__class_weight": [None, "balanced"],  # Weighted vs non-weighted classes
            "do_stemming": True,
            "scoring": ['f1'],
        }

        self.__settings[SettingsHandler.INTERNAL_SETTINGS] = {}

    @staticmethod
    def create_chi2_k_value(start, stop, step, all):
        chi2__k = list(range(start, stop, step))  # Set parameter range + step size for Select K best features
        if all:
            chi2__k.append('all')
        return chi2__k
