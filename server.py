import logging.config
import os

import tornado.httpserver
import tornado.web
from healthcheck import HealthCheck, TornadoHandler
from tornado.ioloop import IOLoop

from trivia.handlers import TriviaSessionStartHandler, TriviaSessionResetHandler, TriviaSessionStopHandler, \
    TriviaCategoriesHandler, TriviaQuestionsHandler

MAX_BUFFER_SIZE = 200 * 1024 * 1024  # 200MB
PORT = 8888
LOGGING_CONF_FILE = "logging.ini"

__logger = logging.getLogger(__name__)


def make_http_server(is_from_tests: bool):
    health = HealthCheck()

    if not is_from_tests:
        logging.config.fileConfig(
            fname=LOGGING_CONF_FILE, disable_existing_loggers=False
        )

    environment = os.environ.get("ENVIRONMENT", "dev")
    __logger.info("Setup HTTP Tornado server for env: {}".format(environment))

    paths = [
        (r"/healthcheck", TornadoHandler, dict(checker=health)),
        (r"/session/start", TriviaSessionStartHandler),
        (r"/session/reset", TriviaSessionResetHandler),
        (r"/session/stop", TriviaSessionStopHandler),
        (r"/categories", TriviaCategoriesHandler),
        (r"/questions", TriviaQuestionsHandler),
    ]

    if environment == "prod":
        return make_prod_server(paths)
    else:
        return make_dev_server(paths)


def make_prod_server(paths):
    app = tornado.web.Application(paths)
    server = tornado.httpserver.HTTPServer(app, max_buffer_size=MAX_BUFFER_SIZE)
    server.bind(address="0.0.0.0", port=PORT)
    server.start(0)
    return app


def make_dev_server(paths):
    app = tornado.web.Application(paths, debug=True)
    app.listen(address="0.0.0.0", port=PORT, max_buffer_size=MAX_BUFFER_SIZE)
    return app


def start_http_server():
    make_http_server(is_from_tests=False)
    __logger.info("Starting IOLoop...")
    IOLoop.current().start()


if __name__ == "__main__":
    start_http_server()
