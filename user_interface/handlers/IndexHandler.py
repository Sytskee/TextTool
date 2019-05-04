from tornado.web import RequestHandler


class IndexHandler(RequestHandler):
    def initialize(self, webapp_settings):
        self.webapp_settings = webapp_settings

    def data_received(self, chunk):
        pass

    def get(self):
        self.render("index.html", webapp_settings=self.webapp_settings)
