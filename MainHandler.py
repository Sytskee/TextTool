import inspect
import multiprocessing
import os

import tornado.ioloop
import tornado.queues

from tornado.web import Application
from user_interface.handlers.IndexHandler import IndexHandler
from user_interface.handlers.AppSettingsHandler import AppSettingsHandler
from user_interface.web_sockets.LoggingWebSocket import LoggingWebSocket
from user_interface.web_sockets.SettingsWebSocket import SettingsWebSocket

def make_app():
    current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    AppSettingsHandler(current_path)

    status_report_queue = multiprocessing.Queue()

    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
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
