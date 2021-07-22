from hexa.catalog.models import Tag


def resolve_tags(*_):
    return [tag for tag in Tag.objects.all()]
