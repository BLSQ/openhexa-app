import stringcase
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

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

    created = 0
    updated = 0
    identical = 0

    for result in results:
        # Build a dict of dhis2 values indexed by hexa field name, and replace reference to other items by
        # their FK
        dhis2_values = {}
        for dhis2_name, dhis2_value in result.get_values(instance.hexa_locale).items():
            hexa_name = stringcase.snakecase(dhis2_name)
            # We need to prefix the id field as we already have one on all models
            if hexa_name == "id":
                hexa_name = "dhis2_id"

            dhis2_values[hexa_name] = _match_reference(
                model_class, hexa_name, dhis2_value
            )

        try:
            # Check if the dhis2 data is already in our database and compare values (hexa vs dhis2)
            existing_hexa_item = model_class.objects.get(
                dhis2_id=dhis2_values["dhis2_id"]
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
                existing_hexa_item.hexa_last_synced_at = timezone.now()
                existing_hexa_item.save()
                updated += 1
            else:
                identical += 1
        # If we don't have the DE locally, create it
        except ObjectDoesNotExist:
            model_class.objects.create(
                **dhis2_values,
                instance=instance,
                hexa_last_synced_at=timezone.now(),
            )
            created += 1

    return DatasourceSyncResult(
        datasource=instance,
        created=created,
        updated=updated,
        identical=identical,
    )
