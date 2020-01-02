import inspect
import multiprocessing

import tornado.ioloop
import tornado.queues

from pathlib import Path
from tornado.web import Application
from user_interface.handlers.IndexHandler import IndexHandler
from user_interface.handlers.AppSettingsHandler import AppSettingsHandler
from user_interface.web_sockets.LoggingWebSocket import LoggingWebSocket
from user_interface.web_sockets.SettingsWebSocket import SettingsWebSocket

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
