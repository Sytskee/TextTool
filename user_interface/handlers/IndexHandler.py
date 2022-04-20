from tornado.web import RequestHandler

from user_interface.handlers.SettingsHandler import SettingsHandler


class IndexHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        self.render("index.html", webapp_settings=SettingsHandler().get_settings())
