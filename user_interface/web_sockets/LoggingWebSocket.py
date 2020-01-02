import asyncio
from typing import Any

from concurrent.futures import ThreadPoolExecutor

import tornado.web
from tornado import httputil
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from user_interface.handlers.SettingsHandler import SettingsHandler


class LoggingWebSocket(WebSocketHandler):
    def initialize(self, status_report_queue):
        self.status_report_queue = status_report_queue

        self.io_loop = IOLoop.current()

        self.executor = ThreadPoolExecutor(max_workers=2)
        self.executor.submit(self.get_logging)

        self.__app_settings_handler = SettingsHandler()

    def on_message(self, message):
        self.write_message(u"You said: " + message + "\r\n")

    def data_received(self, chunk):
        pass

    def get_logging(self):
        # Blocking call on queue
        message = self.status_report_queue.get()

        # Use the main IOLoop to publish the message
        self.io_loop.add_callback(self.publish, message)

        # Recursive call to self
        self.executor.submit(self.get_logging)

    def publish(self, message):
        self.write_message(message + "\r\n")

        '''TODO: must be done in a proper way'''
        if message.endswith('All done!'):
            self.__app_settings_handler.set(SettingsHandler.PROGRAM_SETTINGS, "classifier_running", False)
