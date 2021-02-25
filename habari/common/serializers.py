from django.forms import model_to_dict


def serialize_queryset(queryset):
    """Serialize a queryset to a list of dictionaries using django model_to_dict() function, augmented with the
    result class name."""

    return [
        {**model_to_dict(model), "class": model.__class__.__name__}
        for model in queryset
    ]
