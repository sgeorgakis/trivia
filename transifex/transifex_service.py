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


async def upsert_data(category, data):
    resource_id, already_exists = await __upsert_resource(category)
    # if already_exists:
    # patch
    #    pass
    # else:
    request_body = ResourceString(resource_id, str(data))
    await transifex_client.upload_new_file(request_body)
