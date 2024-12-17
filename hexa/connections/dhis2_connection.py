from openhexa.toolbox.dhis2 import DHIS2
from openhexa.toolbox.dhis2.api import DHIS2Connection

from hexa.workspaces.models import Connection, ConnectionField


def get_connection_by_slug(slug: str) -> DHIS2 | None:
    """
    Gets DHIS2 connection from workspace
    """
    dhis2_connection = Connection.objects.filter(slug=slug).first()
    if not dhis2_connection:
        return None

    fields = ConnectionField.objects.filter(connection=dhis2_connection).all()
    dhis_connection_dict = {}

    for field in fields:
        dhis_connection_dict[field.code] = field.value

    return get_dhis2_client(
        dhis_connection_dict["url"],
        dhis_connection_dict["username"],
        dhis_connection_dict["password"],
    )


# TODO: modify toolbox to accept strings instead of connection object
def get_dhis2_client(url: str, username: str, password: str) -> DHIS2:
    connection = DHIS2Connection(username, password, url)
    return DHIS2(connection)


def get_org_units(dhis2: DHIS2, fields: str | None, filter: str | None) -> dict:
    """
    Gets all organisation units from DHIS2
    """
    dhis2.meta.organisation_units()
