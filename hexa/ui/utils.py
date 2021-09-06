def get_item_value(item, accessor, *, container, exclude):
    if hasattr(container, accessor):
        attr = getattr(container, accessor)
        if callable(attr):
            return attr(item)
        elif isinstance(attr, property):
            return attr.fget()
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
