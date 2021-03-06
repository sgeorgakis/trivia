import logging.config
import os
from abc import ABC

import tornado.escape
from dotenv import load_dotenv

from tornado import httpclient
from tornado.httpclient import HTTPError

load_dotenv()

API_KEY = os.getenv("TRANSIFEX_API_KEY")
API_PATH = "https://rest.api.transifex.com"
PROJECT_ID = os.getenv("TRANSIFEX_PROJECT_ID")
API_JSON_CONTENT_TYPE = "application/vnd.api+json"

logger = logging.getLogger(__name__)


class TransifexClient(ABC):
    async def list_resources(self):
        pass

    async def create_resource(self, resource):
        pass

    async def delete_resource(self, resource_id):
        pass

    async def upload_new_file(self, data):
        pass

    async def get_resource_strings(self, resource_id):
        pass

    async def get_cursor_resource_strings(self, path):
        pass


class MockTransifexClient(TransifexClient):
    async def list_resources(self):
        return {"1": "resource1"}

    async def create_resource(self, resource):
        return "id"

    async def get_resource_strings(self, resource_id):
        return [
            {
                "attributes": {
                    "key": "question",
                    "strings": {"other": "This is a question"},
                }
            }
        ], "url"

    async def get_cursor_resource_strings(self, path):
        return [
            {
                "attributes": {
                    "key": "question2",
                    "strings": {"other": "This is another question"},
                }
            }
        ], None


class TransifexClientImpl(TransifexClient):
    def __init__(self):
        self.__client = httpclient.AsyncHTTPClient()

    async def delete_resource(self, resource_id):
        try:
            request = httpclient.HTTPRequest(
                "{}/resources/{}".format(API_PATH, resource_id),
                method="DELETE",
                headers=self.__set_authorization_header(),
            )
            response = await self.__client.fetch(request)
        except HTTPError as e:
            logger.error(
                "Error while deleting resource {} from Transifex API. Code: {}, message: {}".format(
                    resource_id, e.code, tornado.escape.json_decode(e.response.body)
                )
            )
            raise e

    async def list_resources(self):
        try:
            path = "{}/resources?filter[project]={}".format(API_PATH, PROJECT_ID)
            logger.debug("Path for list resources request {}".format(path))
            request = httpclient.HTTPRequest(
                path, method="GET", headers=self.__set_authorization_header()
            )
            response = await self.__client.fetch(request)
            response_json = tornado.escape.json_decode(response.body)
        except HTTPError as e:
            logger.error(
                "Error while requesting list resources from Transifex API. Code: {}, message: {}".format(
                    e.code, tornado.escape.json_decode(e.response.body)
                )
            )
            raise e
        response_dictionary = {}
        for element in response_json["data"]:
            response_dictionary[element["attributes"]["name"]] = element["id"]
        return response_dictionary

    async def create_resource(self, resource):
        try:
            headers = self.__set_authorization_header()
            headers["Content-Type"] = API_JSON_CONTENT_TYPE
            logger.debug("New Resource: {}".format(resource.to_json()))
            request = httpclient.HTTPRequest(
                "{}/resources".format(API_PATH),
                method="POST",
                headers=headers,
                body=resource.to_json(),
            )
            response = await self.__client.fetch(request)
            response_json = tornado.escape.json_decode(response.body)
        except HTTPError as e:
            logger.error(
                "Error while requesting list resources from Transifex API. Code {}:, message: {}".format(
                    e.code, tornado.escape.json_decode(e.response.body)
                )
            )
            raise e
        return response_json["data"]["id"]

    async def upload_new_file(self, data):
        try:
            logger.debug("Uploading new file. Body: {}".format(data.to_json()))
            headers = self.__set_authorization_header()
            headers["Content-Type"] = API_JSON_CONTENT_TYPE
            request = httpclient.HTTPRequest(
                "{}/resource_strings_async_uploads".format(API_PATH),
                method="POST",
                headers=headers,
                body=data.to_json(),
            )
            response = await self.__client.fetch(request)
        except HTTPError as e:
            logger.error(
                "Error while requesting list resources from Transifex API. Code: {}, message: {}".format(
                    e.code, tornado.escape.json_decode(e.response.body)
                )
            )
            raise e
        logger.debug(
            "Response code: {}, Response body: {}".format(
                response.code, tornado.escape.json_decode(response.body)
            )
        )

    async def get_resource_strings(self, resource_id):
        try:
            request = httpclient.HTTPRequest(
                "{}/resource_strings?filter[resource]={}".format(API_PATH, resource_id),
                method="GET",
                headers=self.__set_authorization_header(),
            )
            response = await self.__client.fetch(request)
            response_json = tornado.escape.json_decode(response.body)
        except HTTPError as e:
            logger.error(
                "Error while requesting list resource strings from Transifex API. Code: {}, message: {}".format(
                    e.code, tornado.escape.json_decode(e.response.body)
                )
            )
            raise e
        return response_json["data"], response_json["links"]["next"]

    async def get_cursor_resource_strings(self, path):
        try:
            request = httpclient.HTTPRequest(
                path, method="GET", headers=self.__set_authorization_header()
            )
            response = await self.__client.fetch(request)
            response_json = tornado.escape.json_decode(response.body)
        except HTTPError as e:
            logger.error(
                "Error while requesting list resource strings from Transifex API. Code: {}, message: {}".format(
                    e.code, tornado.escape.json_decode(e.response.body)
                )
            )
            raise e
        return response_json["data"], response_json["links"]["next"]

    def __set_authorization_header(self):
        return {"Authorization": "Bearer {}".format(API_KEY)}
