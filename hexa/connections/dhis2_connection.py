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


# TODO: modify toolbox to accept connection strings instead of connection object
def get_dhis2_client(url: str, username: str, password: str) -> DHIS2:
    connection = ConcreteDHIS2Connection(url, username, password)
    dhis2_client = DHIS2(connection)
    print(dhis2_client.__dict__)
    return dhis2_client


def get_dhis2_metadata(dhis2: DHIS2, type: str, **kwargs) -> dict:
    """
    Gets metadata from DHIS2
    """
    metadata_methods = {
        # TODO: extend toolbox client with fields
        "organisation_units": dhis2.meta.organisation_units,
        # TODO: extend with fields and filter - or addd name to id dictionary
        "organisation_unit_groups": dhis2.meta.organisation_unit_groups,
        # all good
        "organisation_unit_levels": dhis2.meta.organisation_unit_levels,
        # already ahs dataElements by id
        "datasets": dhis2.meta.datasets,
        # all good, use filter to filter on dataSets, or dataElementGroups
        "data_elements": dhis2.meta.data_elements,
        # already has dataElements, but without names, better first list of ids to build
        "data_element_groups": dhis2.meta.data_element_groups,
        # indicator
        "indicator": dhis2.meta.indicators,
        "indicator_groups": dhis2.meta.indicator_groups,
    }
    return metadata_methods[type](**kwargs)
