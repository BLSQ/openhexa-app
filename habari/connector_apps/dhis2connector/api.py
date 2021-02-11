import datetime

from dhis2 import Api
from django.utils import timezone, dateparse


class Dhis2Result:
    """Base class for DHIS2 result items - handles translations"""

    # Mapping dhis2 field name -> field type, field default
    FIELD_SPECS = {
        "id": (str, None),
        "name": (str, None),
        "shortName": (str, None),
        "description": (str, ""),
        "externalAccess": (bool, None),
        "favorite": (bool, None),
        "created": (datetime.datetime, None),
        "lastUpdated": (datetime.datetime, None),
    }

    def __init__(self, data):
        self._data = data

    @property
    def fields(self):
        return {**Dhis2Result.FIELD_SPECS, **self.FIELD_SPECS}

    def get_values(self, locale=None):
        return {
            field_name: self.get_value(field_name, locale) for field_name in self.fields
        }

    def get_value(self, field_name, locale=None):
        try:
            field_type, field_default = self.fields[field_name]
        except KeyError:
            raise ValueError(
                f'The "{field_name}" field does not exist in {self.__class__.__name__}'
            )

        # If "dict" type, references another record - return as is (or default)
        if field_type is dict:
            return self._data.get(field_name, {"id": field_default})

        # If "datetime" type, convert to time-aware datetime
        if field_type is datetime.datetime:
            return timezone.make_aware(
                dateparse.parse_datetime(self._data.get(field_name, field_default))
            )

        # If not a translated property (or no translations), early return
        if "translations" not in self._data or not any(
            p for p in self._data["translations"] if p["property"] == field_name.upper()
        ):
            return self._data.get(field_name, field_default)

        try:
            # Attempt to extract the translated value for the provided locale (which can be None)
            return next(
                p
                for p in self._data["translations"]
                if p["property"] == field_name.upper()
                # If locale is None, the first description will be returned
                and (locale is None or locale in p["locale"])
            )["value"]
        except StopIteration:
            if (
                locale is None
            ):  # Locale is None: if no description at all, return the default
                return field_default

            # Could not find a description for the provided locale, find any description
            return self.get_value(field_name, None)


class Dhis2DataElementResult(Dhis2Result):
    FIELD_SPECS = {
        "code": (str, ""),
        "domainType": (str, None),
        "valueType": (str, None),
        "aggregationType": (str, None),
    }


class Dhis2IndicatorTypeResult(Dhis2Result):
    FIELD_SPECS = {
        "number": (bool, None),
        "factor": (int, None),
    }


class Dhis2IndicatorResult(Dhis2Result):
    FIELD_SPECS = {
        "code": (str, ""),
        "indicatorType": (dict, None),
        "annualized": (bool, None),
    }


class Dhis2Client:
    def __init__(self, *, url, username, password):
        self._api = Api(url, username, password)

    def fetch_data_elements(self):
        return [
            Dhis2DataElementResult(data)
            for data in self._api.get_paged(
                "dataElements", params={"fields": ":all"}, page_size=100, merge=True
            )["dataElements"]
        ]

    def fetch_indicator_types(self):
        return [
            Dhis2IndicatorTypeResult(data)
            for data in self._api.get_paged(
                "indicatorTypes", params={"fields": ":all"}, page_size=100, merge=True
            )["indicatorTypes"]
        ]

    def fetch_indicators(self):
        return [
            Dhis2IndicatorResult(data)
            for data in self._api.get_paged(
                "indicators", params={"fields": ":all"}, page_size=100, merge=True
            )["indicators"]
        ]
