import unittest

import pytest

from transifex.client.transifex_client import MockTransifexClient
from transifex.transifex_service import TransifexService


class TestTransifexService(unittest.TestCase):
    @pytest.mark.asyncio
    async def test_upsert_resource(self):
        client = MockTransifexClient()
        service = TransifexService(client)
        resource_id, data = await service.upsert_resource("1")
        self.assert_(isinstance(data, dict))
        self.assert_("question" in data)
        self.assert_("question2" in data)
