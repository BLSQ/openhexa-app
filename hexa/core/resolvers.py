from hexa.catalog.models import Tag


def resolve_tags(obj, *_):
    return [tag for tag in obj.tags.all()]
