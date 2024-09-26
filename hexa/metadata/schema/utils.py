from django.contrib.contenttypes.models import ContentType

from hexa.metadata.models import OpaqueId


def get_model_instance(id: str):
    """
    Get a model instance by its id.
    """
    instance_id, model_type = OpaqueId.decode_base64_id(id)
    app_label, model = model_type.split(".")
    content_type = ContentType.objects.get(
        app_label=app_label.lower(), model=model.lower()
    )
    model_class = content_type.model_class()
    model_instance = model_class.objects.get(id=instance_id)
    return model_class, model_instance
