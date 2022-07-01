import json
import logging
import sys
import traceback

import tornado.web

from trivia.client import trivia_client
from trivia.client.models import NoActiveSessionError

logger = logging.getLogger(__name__)


class TriviaSessionStartHandler(tornado.web.RequestHandler):
    async def post(self):
        logger.debug("Got request for starting session")
        await trivia_client.start_session()


class TriviaSessionStopHandler(tornado.web.RequestHandler):
    async def post(self):
        logger.debug("Got request for stopping session")
        trivia_client.stop_session()


class TriviaSessionResetHandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            logger.debug("Got request for reseting session")
            await trivia_client.reset_session()
        except NoActiveSessionError as e:
            logger.error("Error while reseting session: {}".format(e))
            logger.error(traceback.format_exception(*sys.exc_info()))
            self.clear()
            self.write(json.dumps({"message": str(e)}))
            self.set_status(400)
            self.clear_header("Content-Type")
            self.add_header("Content-Type", "application/json")


class TriviaCategoriesHandler(tornado.web.RequestHandler):
    async def get(self):
        logger.debug("Got request for fetching all trivia categories")
        categories = await trivia_client.list_categories()
        self.clear()
        self.write(json.dumps(categories))
        self.clear_header("Content-Type")
        self.add_header("Content-Type", "application/json")


class TriviaQuestionsHandler(tornado.web.RequestHandler):
    async def get(self):
        logger.debug(
            "Got request for getting questions. Amount: {}, Categories: {}".format(
                self.request.arguments["amount"], self.request.arguments["category"]
            )
        )
