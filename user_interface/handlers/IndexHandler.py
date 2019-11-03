from tornado.web import RequestHandler

from user_interface.handlers.AppSettingsHandler import AppSettingsHandler


class IndexHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        self.render("index.html", webapp_settings=AppSettingsHandler().get_app_settings())
