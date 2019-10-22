import asyncio
from typing import Any

from concurrent.futures import ThreadPoolExecutor

import tornado.web
from tornado import httputil
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler


class LoggingWebSocket(WebSocketHandler):
    def initialize(self, webapp_settings, status_report_queue):
        self.webapp_settings = webapp_settings
        self.status_report_queue = status_report_queue

        self.io_loop = IOLoop.current()

        self.executor = ThreadPoolExecutor(max_workers=2)
        self.executor.submit(self.get_logging)

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
