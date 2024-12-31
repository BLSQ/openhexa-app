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


def query_dhis2_metadata(dhis2: DHIS2, type: str, **kwargs) -> dict:
    """
    Gets metadata from DHIS2
    """
    type_to_metadata_method = {
        "organisationUnits": dhis2.meta.organisation_units,
        "organisationUnitGroups": dhis2.meta.organisation_unit_groups,
        "organisationUnitLevels": dhis2.meta.organisation_unit_levels,
        "datasets": dhis2.meta.datasets,
        "dataElements": dhis2.meta.data_elements,
        "dataElementGroups": dhis2.meta.data_element_groups,
        "indicators": dhis2.meta.indicators,
        "indicatorGroups": dhis2.meta.indicator_groups,
    }
    return type_to_metadata_method[type](**kwargs)
