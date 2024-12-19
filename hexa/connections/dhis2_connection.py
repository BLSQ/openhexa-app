from openhexa.toolbox.dhis2 import DHIS2

from hexa.workspaces.models import Connection, ConnectionField


class ConcreteDHIS2Connection:
    def __init__(self, url: str, username: str, password: str):
        self.username = username
        self.password = password
        self.url = url


def get_client_by_slug(slug: str) -> DHIS2 | None:
    """
    Gets DHIS2 connection from workspace
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

    return get_dhis2_client(
        url=dhis_connection_dict["url"],
        username=dhis_connection_dict["username"],
        password=dhis_connection_dict["password"],
    )


# TODO: modify toolbox to accept strings instead of connection object
def get_dhis2_client(url: str, username: str, password: str) -> DHIS2:
    connection = ConcreteDHIS2Connection(url, username, password)
    dhis2_client = DHIS2(connection)
    print(dhis2_client.__dict__)
    return dhis2_client


def get_dhis2_metadata(
    dhis2: DHIS2, type: str, fields: str, filter: str | None
) -> dict:
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

    return metadata_methods[type](fields=fields, filter=filter)
