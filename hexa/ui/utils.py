from django.utils.translation import ugettext_lazy as _


def get_item_value(item, accessor, *, container=None, exclude=None):
    container_class = type(container)

    if isinstance(accessor, StaticText):
        return accessor

    if container is not None and hasattr(container, accessor):
        attr = getattr(container_class, accessor)
        if callable(attr):
            return getattr(container, accessor)(item)
        elif isinstance(attr, property):
            return getattr(container, accessor)
        elif exclude is None or not isinstance(attr, exclude):
            return attr

    paths = accessor.split(".")
    item_value = item
    for path in paths:
        if hasattr(item_value, path):
            item_value = getattr(item_value, path)
        else:
            item_value = None
            break
    if callable(item_value):
        item_value = item_value()
    if item_value is not None:
        return item_value

    return None


class StaticText:
    def __init__(self, text):
        self.text = _(text)

    def __str__(self):
        return str(self.text)
