from tornado.escape import json_decode
from tornado.testing import AsyncHTTPTestCase

import server


class TestTornadoServer(AsyncHTTPTestCase):
    def get_app(self):
        return server.make_http_server(is_from_tests=True)

    def test_healthcheck(self):
        response = self.fetch("/healthcheck")
        self.assertEqual(response.code, 200)

    def test_reset_session_with_empty_session(self):
        response = self.fetch("/session/reset")
        self.assertEqual(response.code, 400)

    def test_session_start(self):
        response = self.fetch("/session/start")
        self.assertEqual(response.code, 200)

    def test_session_stop(self):
        response = self.fetch("/session/stop")
        self.assertEqual(response.code, 200)

    def test_get_categories(self):
        response = self.fetch("/categories")
        self.assertEqual(response.code, 200)
        self.assert_(isinstance(json_decode(response.body), list))
