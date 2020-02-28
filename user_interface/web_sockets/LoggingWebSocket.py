from concurrent.futures import ThreadPoolExecutor
from queue import Empty
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler, WebSocketClosedError
from user_interface.handlers.SettingsHandler import SettingsHandler


class LoggingWebSocket(WebSocketHandler):
    def initialize(self, status_report_queue):
        self.status_report_queue = status_report_queue

        self.io_loop = IOLoop.current()

        self.executor = ThreadPoolExecutor(max_workers=2)
        self.executor.submit(self.get_logging)

        self.__app_settings_handler = SettingsHandler()
        self.is_closed = False

    def on_message(self, message):
        self.write_message(u"You said: " + message + "\r\n")

    def on_close(self):
        self.is_closed = True
        self.executor.shutdown(wait=False)
        print("LoggingWebSocket closed")

    def data_received(self, chunk):
        pass

    def get_logging(self):
        try:
            # Blocking call on queue
            message = self.status_report_queue.get(timeout=1)

            # Use the main IOLoop to publish the message
            self.io_loop.add_callback(self.publish, message)
        except Empty:
            # Ignore timeout and keep trying until connection is closed
            pass

        if not self.is_closed:
            # Recursive call to self
            self.executor.submit(self.get_logging)

    def publish(self, message):
        try:
            self.write_message(message + "\r\n")
        except WebSocketClosedError as err:
            print('WebSocketClosedError: {0}'.format(err))

        '''TODO: must be done in a proper way'''
        if message.endswith('All done!'):
            self.__app_settings_handler.set(SettingsHandler.PROGRAM_SETTINGS, "classifier_running", False)
