import stringcase
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

from hexa.catalog.sync import DatasourceSyncResult


def _match_reference(model_class, hexa_name, dhis2_value):
    # No dict? Then return as is
    if not isinstance(dhis2_value, dict):
        return dhis2_value

    # Otherwise, fetch referenced model
    field_info = getattr(model_class, hexa_name)
    related_model = field_info.field.related_model

    try:
        return related_model.objects.get(dhis2_id=dhis2_value["id"])
    except related_model.DoesNotExist:
        return None


def sync_from_dhis2_results(*, model_class, instance, results):
    """Iterate over the DEs in the response and create, update or ignore depending on local data"""

    model_name = model_class._meta.model_name
    instance.sync_log(
        "start sync_from_dhis2_results model %s, results %s", model_name, len(results)
    )

    created = 0
    updated = 0
    identical = 0

    for i, result in enumerate(results):
        instance.sync_log(
            "loop sync_from_dhis2_results model %s, position %s, results %s, created %s, updated %s, identical %s",
            model_name,
            i,
            result.get_value("id"),
            created,
            updated,
            identical,
        )
        # Build a dict of dhis2 values indexed by hexa field name, and replace reference to other items by
        # their FK
        dhis2_values = {}
        for dhis2_name, dhis2_value in result.get_values(instance.locale).items():
            hexa_name = stringcase.snakecase(dhis2_name)
            if dhis2_name == "id":
                hexa_name = "dhis2_id"

            dhis2_values[hexa_name] = _match_reference(
                model_class, hexa_name, dhis2_value
            )

        try:
            # Check if the dhis2 data is already in our database and compare values (hexa vs dhis2)
            existing_hexa_item = model_class.objects.get(
                dhis2_id=dhis2_values["dhis2_id"],
                instance=instance,
            )
            existing_hexa_values = {
                hexa_name: getattr(existing_hexa_item, hexa_name)
                for hexa_name in dhis2_values
            }
            diff_values = {
                hexa_name: dhis2_value
                for hexa_name, dhis2_value in dhis2_values.items()
                if dhis2_value != existing_hexa_values[hexa_name]
            }

            # Check if we need to actually update the local version
            if len(diff_values) > 0:
                for hexa_name in diff_values:
                    setattr(
                        existing_hexa_item,
                        hexa_name,
                        diff_values[hexa_name],
                    )
                existing_hexa_item.save()
                updated += 1
            else:
                identical += 1
            hexa_item = existing_hexa_item
        # If we don't have the DE locally, create it
        except ObjectDoesNotExist:
            hexa_item = model_class.objects.create(
                **dhis2_values,
                instance=instance,
            )
            created += 1

        instance.sync_log(
            "acted sync_from_dhis2_results model %s, position %s, results %s, created %s, updated %s, identical %s",
            model_name,
            i,
            result.get_value("id"),
            created,
            updated,
            identical,
        )

        for relation, items in result.get_relations().items():
            instance.sync_log(
                "relation sync_from_dhis2_results model %s, relation %s, items %s",
                model_name,
                relation.model_name,
                items,
            )
            model = apps.get_model("connector_dhis2", relation.model_name)
            items = model.objects.filter(dhis2_id__in=items)
            getattr(hexa_item, relation.model_field).set(items)

    return DatasourceSyncResult(
        datasource=instance,
        created=created,
        updated=updated,
        identical=identical,
    )
