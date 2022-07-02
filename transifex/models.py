import json


class Resource:
    def __init__(self, name, slug, project_id):
        self.data = ResourceData(name, slug, project_id)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class ResourceData:
    def __init__(self, name, slug, project_id):
        self.attributes = ResourceAttributes(name, slug)
        self.relationships = ResourceRelationships(project_id)
        self.type = "resources"


class ResourceAttributes:
    def __init__(self, name, slug):
        self.accept_translations = True
        self.name = name
        self.slug = slug
        self.categories = ["trivia"]


class ResourceRelationships:
    def __init__(self, resource_id):
        self.i18n_format = I18NFormat()
        self.project = {"data": {"id": resource_id, "type": "projects"}}


class I18NFormat:
    def __init__(self):
        self.data = {"id": "KEYVALUEJSON", "type": "i18n_formats"}


class ResourceString:
    def __init__(self, resource_id, content):
        self.data = ResourceStringData(resource_id, content)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class ResourceStringData:
    def __init__(self, resource_id, content):
        self.attributes = ResourceStringAttributes(content)
        self.relationships = ResourceStringRelationships(resource_id)
        self.type = "resource_strings_async_uploads"


class ResourceStringAttributes:
    def __init__(self, content):
        self.content = content
        self.content_encoding = "text"
        self.replace_edited_strings = False


class ResourceStringRelationships:
    def __init__(self, resource_id):
        self.resource = {"data": {"id": resource_id, "type": "resources"}}
