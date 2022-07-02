import json
import logging
import sys
import traceback

import tornado.web

from trivia.client.models import NoActiveSessionError
from trivia.models import TriviaQuestion

logger = logging.getLogger(__name__)


class TriviaSessionStartHandler(tornado.web.RequestHandler):
    def initialize(self, trivia_client):
        self.__trivia_client = trivia_client

    async def post(self):
        logger.debug("Got request for starting session")
        await self.__trivia_client.start_session()


class TriviaSessionStopHandler(tornado.web.RequestHandler):
    def initialize(self, trivia_client):
        self.__trivia_client = trivia_client

    async def post(self):
        logger.debug("Got request for stopping session")
        self.__trivia_client.stop_session()


class TriviaSessionResetHandler(tornado.web.RequestHandler):
    def initialize(self, trivia_client):
        self.__trivia_client = trivia_client

    async def post(self):
        try:
            logger.debug("Got request for reseting session")
            await self.__trivia_client.reset_session()
        except NoActiveSessionError as e:
            logger.error("Error while reseting session: {}".format(e))
            logger.error(traceback.format_exception(*sys.exc_info()))
            self.clear()
            self.write(json.dumps({"message": str(e)}))
            self.set_status(400)
            self.clear_header("Content-Type")
            self.add_header("Content-Type", "application/json")


class TriviaCategoriesHandler(tornado.web.RequestHandler):
    def initialize(self, trivia_client):
        self.__trivia_client = trivia_client

    async def get(self):
        logger.debug("Got request for fetching all trivia categories")
        categories = await self.__trivia_client.list_categories()
        self.clear()
        self.write(json.dumps(categories))
        self.clear_header("Content-Type")
        self.add_header("Content-Type", "application/json")


class TriviaQuestionsHandler(tornado.web.RequestHandler):
    def initialize(self, trivia_client, transifex_service):
        self.__trivia_client = trivia_client
        self.__transifex_service = transifex_service

    async def post(self):
        if "amount" in self.request.arguments:
            number_of_questions = int(
                self.request.arguments["amount"][0].decode("utf-8")
            )
        else:
            number_of_questions = 10
        categories = [cat.decode("utf-8") for cat in self.request.arguments["category"]]
        if len(categories) == 0:
            self.write(json.dumps({"message": "Missing path parameter category"}))
            self.set_status(400)
            self.clear_header("Content-Type")
            self.add_header("Content-Type", "application/json")
        else:
            logger.debug(
                "Got request for fetching and uploading questions. Amount: {}, Categories: {}".format(
                    number_of_questions, categories
                )
            )
            for category in categories:
                questions = await self.__trivia_client.get_questions(
                    category, number_of_questions
                )
                trivia_questions = [TriviaQuestion(question) for question in questions]
                await self.__transifex_service.upsert_data(category, trivia_questions)
                self.clear()
                self.set_status(202)
