import os

from dotenv import load_dotenv

from transifex.client.transifex_client import TransifexClientImpl, MockTransifexClient

load_dotenv()


def create_transifex_client():
    if os.getenv("ENVIRONMENT") != "test":
        return TransifexClientImpl()
    else:
        return MockTransifexClient()


transifex_client = create_transifex_client()
