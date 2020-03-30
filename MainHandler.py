import inspect
import json
import multiprocessing

import tornado.ioloop
import tornado.queues

from joblib import parallel_backend
from pathlib import Path
from tornado.web import Application
from user_interface.handlers.IndexHandler import IndexHandler
from user_interface.handlers.SettingsHandler import SettingsHandler
from user_interface.web_sockets.LoggingWebSocket import LoggingWebSocket
from user_interface.web_sockets.SettingsWebSocket import SettingsWebSocket


def merge_config(config_target, config_loaded):
    for k, v in config_loaded.items():
        if isinstance(v, dict) and k in config_target:
            merge_config(config_target[k], config_loaded[k])
        else:
            config_target[k] = config_loaded[k]


def make_app(config_local, current_path_local, config_file_path_local):
    status_report_queue = multiprocessing.Queue()

    SettingsHandler(current_path_local, status_report_queue, config_local, config_file_path_local)

    # Read config after giving AppSettingsHandler the config to set the default values
    with open(config_file_path, 'r') as configfile_local:
        try:
            loaded_config = json.load(configfile_local)
            merge_config(config_local, loaded_config)
        except ValueError as err:
            status_report_queue.put("Loading of settings failed: {}".format(err))

    settings = {
        "template_path": current_path_local.joinpath("templates"),
        "static_path": current_path_local.joinpath("static"),
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


# Always set parallel backend to multiprocessing for support with freezing
parallel_backend('multiprocessing')

if __name__ == "__main__":
    # PyInstaller: When using the multiprocessing module, you must call the following straight after the main check
    multiprocessing.freeze_support()

    current_path = Path(inspect.getfile(inspect.currentframe())).resolve().parent
    config_path = current_path.joinpath("config")
    config_path.mkdir(parents=True, exist_ok=True)

    config_file_path = config_path.joinpath("config.json")
    if not config_file_path.is_file():
        config_file_path.write_text(data="{}", encoding="UTF-8")

    config = {}

    app = make_app(config, current_path, config_file_path)
    print("Start listening on port 8888")
    app.listen(8888)

    tornado.ioloop.IOLoop.current().start()

    app.status_report_queue.close()
