import json
import logging

from transifex.client.transifex_client import TransifexClient, PROJECT_ID
from transifex.models import Resource, ResourceString

transifex_client = TransifexClient()
logger = logging.getLogger(__name__)


async def __upsert_resource(category):
    resources = await transifex_client.list_resources()
    logger.debug("Got resources: {}. Selected category: {}".format(resources, category))
    if category in resources:
        return resources[category], True
    else:
        new_resource = Resource(name=category, slug=category, project_id=PROJECT_ID)
        return await transifex_client.create_resource(new_resource), False


async def upsert_data(category, trivia_questions):
    resource_id, already_exists = await __upsert_resource(category)
    if already_exists:
        #  patch
        pass
    else:
        request_body = ResourceString(
            resource_id, transform_questions(trivia_questions)
        )
        await transifex_client.upload_new_file(request_body)


def transform_questions(trivia_questions):
    dictionary = {}
    for question in trivia_questions:
        for i in range(len(question.incorrect_answers)):
            key = "incorrect_answer_{}_{}".format(i, question.question)
            dictionary[key] = question.incorrect_answers[i]

        correct_answer_key = "correct_answer_{}".format(question.question)
        dictionary[correct_answer_key] = question.correct_answer

        question_key = "question_{}".format(question.question)
        dictionary[question_key] = question.question

    return str(json.dumps(dictionary))
