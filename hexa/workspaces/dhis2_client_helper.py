from enum import Enum

from openhexa.toolbox.dhis2 import DHIS2

from hexa.user_management.models import User
from hexa.workspaces.models import Connection


def get_client_by_slug(slug: str, user: User) -> DHIS2 | None:
    """
    Gets DHIS2 client from workspace by its slug
    """
    try:
        dhis2_connection = (
            Connection.objects.filter_for_user(user).filter(slug=slug).first()
        )
    except Connection.DoesNotExist:
        return None

    if not dhis2_connection:
        return None

    fields = dhis2_connection.fields.all()
    dhis_connection_dict = {field.code: field.value for field in fields}

    return DHIS2(
        url=dhis_connection_dict.get("url"),
        username=dhis_connection_dict.get("username"),
        password=dhis_connection_dict.get("password"),
    )


class DHIS2MetadataQueryType(Enum):
    ORGANISATION_UNITS = "ORGANISATION_UNITS"
    ORGANISATION_UNIT_GROUPS = "ORGANISATION_UNIT_GROUPS"
    ORGANISATION_UNIT_LEVELS = "ORGANISATION_UNIT_LEVELS"
    DATASETS = "DATASETS"
    DATA_ELEMENTS = "DATA_ELEMENTS"
    DATA_ELEMENT_GROUPS = "DATA_ELEMENT_GROUPS"
    INDICATORS = "INDICATORS"
    INDICATOR_GROUPS = "INDICATOR_GROUPS"


def query_dhis2_metadata(dhis2: DHIS2, type: str, **kwargs) -> dict:
    """
    Gets metadata from DHIS2
    """
    metadata_methods = {
        DHIS2MetadataQueryType.ORGANISATION_UNITS.value: dhis2.meta.organisation_units,
        DHIS2MetadataQueryType.ORGANISATION_UNIT_GROUPS.value: dhis2.meta.organisation_unit_groups,
        DHIS2MetadataQueryType.ORGANISATION_UNIT_LEVELS.value: dhis2.meta.organisation_unit_levels,
        DHIS2MetadataQueryType.DATASETS.value: dhis2.meta.datasets,
        DHIS2MetadataQueryType.DATA_ELEMENTS.value: dhis2.meta.data_elements,
        DHIS2MetadataQueryType.DATA_ELEMENT_GROUPS.value: dhis2.meta.data_element_groups,
        DHIS2MetadataQueryType.INDICATORS.value: dhis2.meta.indicators,
        DHIS2MetadataQueryType.INDICATOR_GROUPS.value: dhis2.meta.indicator_groups,
    }
    return metadata_methods[type](**kwargs)