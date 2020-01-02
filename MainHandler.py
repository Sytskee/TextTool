import inspect
import multiprocessing

import tornado.ioloop
import tornado.queues

from configparser import ConfigParser
from nltk.corpus import stopwords
from pathlib import Path
from tornado.web import Application
from user_interface.handlers.IndexHandler import IndexHandler
from user_interface.handlers.AppSettingsHandler import AppSettingsHandler
from user_interface.web_sockets.LoggingWebSocket import LoggingWebSocket
from user_interface.web_sockets.SettingsWebSocket import SettingsWebSocket


def create_fixed_config(config):
    fixed_settings = "fixed"
    config.set(fixed_settings, "software_version", "0.2")


def set_default_text_classifier_settings(config):
    text_classifier_settings = "TextClassifier"
    config.set(text_classifier_settings, "text__vect__min_df",
               [1, 2, 3]) # Number of training documents a term should occur in
    config.set(text_classifier_settings, "text__vect__ngram_range",
               [(1, 1), (2, 2), (3, 3), (1, 3)]) # Test uni-, bi-, tri-, or N-multigrams ranging from 1-3
    config.set(text_classifier_settings, "text__vect__stop_words",
               [stopwords.words(config.get(AppSettingsHandler.APP_SETTINGS, "language")), None])  # Do/do not remove stopwords
    config.set(text_classifier_settings, "text__tfidf__use_idf", [True, False]) # Weight terms by tf or tfidf

    chi2__k = list(range(10, 501, 20))  # Set parameter range + step size for Select K best features
    chi2__k.append('all')

    config.set(text_classifier_settings, "chi2__k", chi2__k) # Select K most informative features
    config.set(text_classifier_settings, "clf__C", [1, 2, 3, 10, 100, 1000])  # Compare different values for C parameter
    config.set(text_classifier_settings, "clf__class_weight", ["balanced"])  # Weighted vs non-weighted classes
    config.set(text_classifier_settings, "do_stemming", True)
    config.set(text_classifier_settings, "scoring", ['f1'])


def make_app():
    current_path = Path(Path.resolve(inspect.getfile(inspect.currentframe())).parent)
    config_path = current_path.joinpath("config")
    config_path.mkdir(parents=True, exist_ok=True)

    status_report_queue = multiprocessing.Queue()
    config = ConfigParser()

    AppSettingsHandler(current_path, status_report_queue, config)
    set_default_text_classifier_settings(config)

    # Read config after giving AppSettingsHandler the config to set the default values
    config.read(config_path.joinpath("config.ini"))

    settings = {
        "template_path": current_path.joinpath("templates"),
        "static_path": current_path.joinpath("static"),
        "debug": True
    }

    return Application(
        [
            (r"/", IndexHandler),
            (r"/index", IndexHandler),
            (r"/api/v1/logging", LoggingWebSocket, dict(status_report_queue=status_report_queue)),
            (r"/api/v1/settings", SettingsWebSocket, dict(status_report_queue=status_report_queue))
        ],
        **settings
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    app.status_report_queue.close()
