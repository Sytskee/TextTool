from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler


class LoggingWebSocket(WebSocketHandler):
    executor = ThreadPoolExecutor(max_workers=2)

    def initialize(self, webapp_settings, status_report_queue):
        self.webapp_settings = webapp_settings
        self.status_report_queue = status_report_queue

        IOLoop.current().add_callback(self.get_logging)

    def on_message(self, message):
        self.write_message(u"You said: " + message + "\r\n")

    def data_received(self, chunk):
        pass

    @run_on_executor
    def get_logging(self):
        self.write_message(self.status_report_queue.get() + "\r\n")
        IOLoop.current().add_callback(self.get_logging)
