import os

from dotenv import load_dotenv

from trivia.client.trivia_client import TriviaClient, TriviaClientImpl, MockTriviaClient

load_dotenv()


def create_trivia_client():
    if os.getenv("ENVIRONMENT") != "test":
        return TriviaClientImpl()
    else:
        return MockTriviaClient()


trivia_client = create_trivia_client()
