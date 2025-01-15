from openhexa.toolbox.dhis2 import DHIS2

from hexa.workspaces.models import Connection


def dhis2_client_from_connection(connection: Connection) -> DHIS2 | None:
    """
    Gets DHIS2 toolbox client from workspace connection
    """
    fields = connection.fields.all()
    dhis_connection_dict = {field.code: field.value for field in fields}

    return DHIS2(
        url=dhis_connection_dict.get("url"),
        username=dhis_connection_dict.get("username"),
        password=dhis_connection_dict.get("password"),
    )


def query_dhis2_metadata(dhis2: DHIS2, type: str, **kwargs) -> dict:
    """
    Gets metadata from DHIS2
    """
    metadata_methods = {
        "ORGANISATION_UNITS": dhis2.meta.organisation_units,
        "ORGANISATION_UNIT_GROUPS": dhis2.meta.organisation_unit_groups,
        "ORGANISATION_UNIT_LEVELS": dhis2.meta.organisation_unit_levels,
        "DATASETS": dhis2.meta.datasets,
        "DATA_ELEMENTS": dhis2.meta.data_elements,
        "DATA_ELEMENT_GROUPS": dhis2.meta.data_element_groups,
        "INDICATORS": dhis2.meta.indicators,
        "INDICATOR_GROUPS": dhis2.meta.indicator_groups,
    }
    return metadata_methods[type](**kwargs)
