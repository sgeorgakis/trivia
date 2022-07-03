import unittest

import pytest

from src.transifex.client.transifex_client import MockTransifexClient
from src.transifex.transifex_service import TransifexService


class TestTransifexService(unittest.TestCase):
    @pytest.mark.asyncio
    async def test_upsert_resource(self):
        client = MockTransifexClient()
        service = TransifexService(client)
        resource_id, data = await service.upsert_resource("1")
        self.assertTrue(isinstance(data, dict))
        self.assertTrue("question" in data)
        self.assertTrue("question2" in data)
