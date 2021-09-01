from django.contrib.contenttypes.models import ContentType

from hexa.catalog.models import (
    Index,
    IndexPermission,
)


def delete_callback(sender, instance, **kwargs):
    datasource = instance.bucket
    index = Index.objects.get(
        content_type=ContentType.objects.get_for_model(datasource),
        object_id=datasource.id,
    )
    index_permission = IndexPermission.objects.first(index=index, team=instance.team)
    index_permission.delete()
