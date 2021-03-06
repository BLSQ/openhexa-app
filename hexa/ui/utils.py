from django.utils.translation import gettext_lazy as _


def get_item_value(item, accessor, *, container=None, exclude=None):
    container_class = type(container)

    if isinstance(accessor, StaticText):
        return accessor

    if container is not None and hasattr(container, accessor):
        attr = getattr(container_class, accessor)
        if callable(attr):
            if item is None:
                return getattr(container, accessor)()
            else:
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
    """Wrapper around gettext_lazy that allows us to mark text as static in data sources - data grids.
    (The datacard / datagrid won't consider it as an accessor and will use it as is).
    """

    def __init__(self, text):
        self.text = _(text)

    def __str__(self):
        return str(self.text)

    def replace(self, a, b):
        return self.text.replace(a, b)
