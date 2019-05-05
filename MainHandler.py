import multiprocessing
import os

import tornado.ioloop
import tornado.queues

from tornado.web import Application
from user_interface.handlers import IndexHandler
from user_interface.web_sockets import LoggingWebSocket, SettingsWebSocket


def make_app():
    webapp_settings = {
        "software_version": "0.2",
        "data_files_path": r"C:\Users\Joost\Desktop\BrievenTest",
        "number_of_classes": -1,
        "classifier_running": False
    }

    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "debug": True
    }

    status_report_queue = multiprocessing.Queue()

    return Application(
        [
            (r"/", IndexHandler.IndexHandler, dict(webapp_settings=webapp_settings)),
            (r"/index", IndexHandler.IndexHandler, dict(webapp_settings=webapp_settings)),
            (r"/api/v1/logging", LoggingWebSocket.LoggingWebSocket,
             dict(webapp_settings=webapp_settings, status_report_queue=status_report_queue)),
            (r"/api/v1/settings", SettingsWebSocket.SettingsWebSocket,
             dict(webapp_settings=webapp_settings, status_report_queue=status_report_queue))
        ],
        **settings
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    app.status_report_queue.close()
