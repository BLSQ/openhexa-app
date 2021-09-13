def get_item_value(item, accessor, *, container=None, exclude=None):
    container_class = type(container)
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
    if item_value is not None:
        return item_value

    return None
