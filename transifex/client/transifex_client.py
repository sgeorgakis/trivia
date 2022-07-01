import logging.config
import os

import tornado.escape
from dotenv import load_dotenv

from tornado import httpclient
from tornado.httpclient import HTTPError

load_dotenv()

API_KEY = os.getenv("TRANSIFEX_API_KEY")
API_PATH = "http://transifex.com"

logger = logging.getLogger(__name__)


class TransifexClient:
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
                    e.status_code,
                    e.message,
                )
            )
            raise e
        self.__check_response_code(response_json)
        self.__token = response_json["token"]
        logger.debug("Got new session token: {}".format(self.__token))