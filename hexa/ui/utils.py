def get_item_value(container, item, accessor, exclude):
    if hasattr(container, accessor):
        attr = getattr(container, accessor)
        if callable(attr):
            return attr(container, item)
        elif isinstance(attr, property):
            return attr.fget(container)
        elif not isinstance(attr, exclude):
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
