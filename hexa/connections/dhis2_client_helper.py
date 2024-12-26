from openhexa.toolbox.dhis2 import DHIS2

from hexa.workspaces.models import Connection, ConnectionField


def get_client_by_slug(slug: str) -> DHIS2 | None:
    """
    Gets DHIS2 client from workspace by its slug
    """
    dhis2_connection = Connection.objects.filter(slug=slug).first()

    if not dhis2_connection:
        return None

    fields = (
        ConnectionField.objects.filter(connection=dhis2_connection)
        .select_related()
        .all()
    )
    dhis_connection_dict = {field.code: field.value for field in fields}

    return DHIS2(
        url=dhis_connection_dict.get("url"),
        username=dhis_connection_dict.get("username"),
        password=dhis_connection_dict.get("password"),
    )


def get_dhis2_metadata(dhis2: DHIS2, type: str, **kwargs) -> dict:
    """
    Gets metadata from DHIS2
    """
    metadata_methods = {
        "organisation_units": dhis2.meta.organisation_units,
        "organisation_unit_groups": dhis2.meta.organisation_unit_groups,
        "organisation_unit_levels": dhis2.meta.organisation_unit_levels,
        "datasets": dhis2.meta.datasets,
        "data_elements": dhis2.meta.data_elements,
        "data_element_groups": dhis2.meta.data_element_groups,
        "indicator": dhis2.meta.indicators,
        "indicator_groups": dhis2.meta.indicator_groups,
    }
    return metadata_methods[type](**kwargs)
