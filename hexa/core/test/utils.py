import datetime


def graphql_datetime_format(dt: datetime.datetime):
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")
