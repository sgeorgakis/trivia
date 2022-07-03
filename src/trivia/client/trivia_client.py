import logging.config
from abc import ABC

import tornado.escape

from tornado import httpclient
from tornado.httpclient import HTTPError

from src.trivia.client.models import NoActiveSessionError

API_PATH = "https://opentdb.com"

response_codes = {
    0: "Success",
    1: "No Results",
    2: "Invalid Parameter",
    3: "Token not found",
    4: "Token empty",
}

logger = logging.getLogger(__name__)


class TriviaClient(ABC):
    async def start_session(self):
        pass

    async def reset_session(self):
        pass

    def stop_session(self):
        pass

    async def list_categories(self):
        pass

    async def get_questions(self, category, number_of_questions=10):
        pass


class MockTriviaClient(TriviaClient):
    def __init__(self):
        self.__token = None

    async def start_session(self):
        self.__token = "1"

    async def reset_session(self):
        if self.__token is None:
            raise NoActiveSessionError("No active session")

    def stop_session(self):
        self.__token = None

    async def list_categories(self):
        return [{1: "Entertainment"}]

    async def get_questions(self, category, number_of_questions=10):
        return [
            {
                "question": "Which of these games was the earliest known first-person shooter with a known time of publication?",
                "correct_answer": "Spasim",
                "incorrect_answers": ["Doom", "Wolfenstein", "Quake"],
            }
        ]


class TriviaClientImpl(TriviaClient):
    def __init__(self):
        self.__token = None
        self.__client = httpclient.AsyncHTTPClient()

    async def start_session(self):
        try:
            request = httpclient.HTTPRequest(
                "{}/api_token.php?command=request".format(API_PATH), method="GET"
            )
            response = await self.__client.fetch(request)
            response_json = tornado.escape.json_decode(response.body)
        except HTTPError as e:
            logger.error(
                "Error while requesting token from trivia API. Code: {}, message: {}".format(
                    e.code, tornado.escape.json_decode(e.response.body)
                )
            )
            raise e
        self.__check_response_code(response_json)
        self.__token = response_json["token"]
        logger.debug("Got new session token: {}".format(self.__token))

    async def reset_session(self):
        if self.__token is None:
            raise NoActiveSessionError("No active session")
        try:
            request = httpclient.HTTPRequest(
                "{}/api_token.php?command=reset&token={}".format(
                    API_PATH, self.__token
                ),
                method="GET",
            )
            response = await self.__client.fetch(request)
            response_json = tornado.escape.json_decode(response.body)
        except HTTPError as e:
            "Error while reseting token from trivia API. Code: {}, message: {}".format(
                e.code, e.text
            )
            raise e
        self.__check_response_code(response_json)
        self.__token = response_json["token"]
        logger.debug("Got new session token: {}".format(self.__token))

    def stop_session(self):
        self.__token = None

    async def list_categories(self):
        try:
            request = httpclient.HTTPRequest(
                "{}/api_category.php".format(API_PATH), method="GET"
            )
            response = await self.__client.fetch(request)
            response_json = tornado.escape.json_decode(response.body)
        except HTTPError as e:
            logger.error(
                "Error while requesting categories from trivia API. Code: {}, message: {}".format(
                    e.code, tornado.escape.json_decode(e.response.body)
                )
            )
            raise e
        return response_json["trivia_categories"]

    async def get_questions(self, category, number_of_questions=10):
        path = "{}/api.php?".format(API_PATH)
        if self.__token is not None:
            path = path + "token={}&".format(self.__token)
        try:
            request = httpclient.HTTPRequest(
                "{}amount={}&category={}".format(path, number_of_questions, category),
                method="GET",
            )
            response = await self.__client.fetch(request)
            response_json = tornado.escape.json_decode(response.body)
        except HTTPError as e:
            logger.error(
                "Error while requesting categories from trivia API. Code: {}, message: {}".format(
                    e.code, tornado.escape.json_decode(e.response.body)
                )
            )
            raise e
        logger.debug("Response for get questions: {}".format(response_json))
        return response_json["results"]

    def __check_response_code(self, response_json):
        response_code = response_json["response_code"]
        if response_json["response_code"] != 0:
            logger.error(
                "Got error response from trivia API. Reason: {}".format(
                    response_codes[response_code],
                )
            )
            raise Exception(
                "Got error response from trivia API. Reason: {}".format(
                    response_codes[response_code]
                )
            )
