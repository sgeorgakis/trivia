import logging.config
import os

import tornado.httpserver
import tornado.web
from healthcheck import HealthCheck, TornadoHandler
from tornado.ioloop import IOLoop

from transifex.client.transifex_client import MockTransifexClient, TransifexClientImpl
from transifex.transifex_service import TransifexService
from trivia.client.trivia_client import TriviaClientImpl, MockTriviaClient
from handlers import (
    TriviaSessionStartHandler,
    TriviaSessionResetHandler,
    TriviaSessionStopHandler,
    TriviaCategoriesHandler,
    TriviaQuestionsHandler,
)

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

    if is_from_tests:
        trivia_client = MockTriviaClient()
        transifex_client = MockTransifexClient()
    else:
        trivia_client = TriviaClientImpl()
        transifex_client = TransifexClientImpl()

    transifex_service = TransifexService(transifex_client)

    paths = [
        (r"/healthcheck", TornadoHandler, dict(checker=health)),
        (
            r"/session/start",
            TriviaSessionStartHandler,
            dict(trivia_client=trivia_client),
        ),
        (
            r"/session/reset",
            TriviaSessionResetHandler,
            dict(trivia_client=trivia_client),
        ),
        (r"/session/stop", TriviaSessionStopHandler, dict(trivia_client=trivia_client)),
        (r"/categories", TriviaCategoriesHandler, dict(trivia_client=trivia_client)),
        (
            r"/questions",
            TriviaQuestionsHandler,
            dict(trivia_client=trivia_client, transifex_service=transifex_service),
        ),
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
