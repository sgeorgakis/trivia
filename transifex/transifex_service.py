import json
import logging

from transifex.client import transifex_client
from transifex.client.transifex_client import PROJECT_ID
from transifex.models import Resource, ResourceString

logger = logging.getLogger(__name__)


async def __upsert_resource(category):
    resources = await transifex_client.list_resources()
    logger.debug("Got resources: {}. Selected category: {}".format(resources, category))
    previous_resource_strings = {}
    if category in resources:
        previous_resource_strings = await __fetch_resource_strings(resources[category])
        await transifex_client.delete_resource(resources[category])
    new_resource = Resource(name=category, slug=category, project_id=PROJECT_ID)
    return await transifex_client.create_resource(new_resource), previous_resource_strings


async def upsert_data(category, trivia_questions):
    resource_id, previous_questions = await __upsert_resource(category)
    transformed_trivia_questions = transform_questions(trivia_questions)
    transformed_trivia_questions.update(previous_questions)
    request_body = ResourceString(
        resource_id, str(json.dumps(transformed_trivia_questions))
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

    return dictionary


async def __fetch_resource_strings(resource_id):
    data, next_path = await transifex_client.get_resource_strings(resource_id)
    resource_strings = __transform_resource_strings(data)
    next_resource_strings = await __get_cursor_resource_strings(next_path)
    resource_strings.update(next_resource_strings)
    return resource_strings


async def __get_cursor_resource_strings(path):
    if path is None:
        return {}
    else:
        resource_strings, next_path = await transifex_client.get_cursor_resource_strings(path)
        transformed_resource_strings = __transform_resource_strings(resource_strings)
        next_resource_strings = await __get_cursor_resource_strings(next_path)
        transformed_resource_strings.update(next_resource_strings)
        return transformed_resource_strings


def __transform_resource_strings(data):
    resource_strings = {}
    for datum in data:
        key = datum["attributes"]["key"]
        value = datum["attributes"]["strings"]["other"]
        resource_strings[key] = value
    return resource_strings
