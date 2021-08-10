from django.contrib.contenttypes.models import ContentType

from hexa.catalog.models import (
    CatalogIndex,
    CatalogIndexPermission,
)


def delete_callback(sender, instance, **kwargs):
    datasource = instance.bucket
    catalog_index = CatalogIndex.objects.get(
        content_type=ContentType.objects.get_for_model(datasource),
        object_id=datasource.id,
    )
    index_permission = CatalogIndexPermission.objects.get(
        catalog_index=catalog_index, team=instance.team
    )
    index_permission.delete()
