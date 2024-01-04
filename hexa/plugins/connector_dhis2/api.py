import datetime
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Callable

from dhis2 import Api
from django.utils import dateparse, timezone

logger = getLogger(__name__)


@dataclass(frozen=True)
class Dhis2Relation:
    """
    describe a m2m relation from an object model to some related items
    """

    # iterable field containing a list of related item
    dhis2_field_name: str
    # callable to extract DHIS2 id from each item of said iterable
    dhis2_extract_id: Callable[[Any], str]
    # OpenHEXA model of the related item
    model_name: str
    # M2M field name in the object model
    model_field: str


class Dhis2Result:
    """Base class for DHIS2 result items - handles translations"""

    # Mapping dhis2 field name -> field type, field default
    FIELD_SPECS = {
        "id": (str, None),
        "name": (str, None),
        "shortName": (str, ""),
        "description": (str, ""),
        "externalAccess": (bool, None),
        "favorite": (bool, None),
        "created": (datetime.datetime, None),
        "lastUpdated": (datetime.datetime, None),
    }

    # Mapping dhis2 field name -> (openhexa model, target field, dhis field name of model)
    RELATIONS: list[Dhis2Relation] = []

    def __init__(self, data):
        self._data = data

    @property
    def fields(self):
        return {**Dhis2Result.FIELD_SPECS, **self.FIELD_SPECS}

    def get_relations(self) -> dict[Dhis2Relation, list]:
        relations = {}
        for relation in self.RELATIONS:
            links = [
                relation.dhis2_extract_id(x)
                for x in self._data.get(relation.dhis2_field_name)
            ]
            relations[relation] = links
        return relations

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
            value = self._data.get(field_name, field_default)
            if value is None:
                # parse_datetime doesn't support None value
                return None
            else:
                return timezone.make_aware(dateparse.parse_datetime(value))

        # If not a translated property (or no translations), early return
        if "translations" not in self._data or not any(
            p for p in self._data["translations"] if p["property"] == field_name.upper()
        ):
            return self._data.get(field_name, field_default)

        if locale is None:
            # find english or derivative
            locale = ("en", "en_GB", "en_US")

        if isinstance(locale, str):
            # if locale only str -> make it iterable
            locale = (locale,)

        # Attempt to extract the translated value for the provided locale
        for translation in self._data["translations"]:
            if (
                translation["property"] == field_name.upper()
                and translation["locale"] in locale
            ):
                return translation["value"]

        return self._data.get(field_name, field_default)


class DataElementResult(Dhis2Result):
    FIELD_SPECS = {
        "code": (str, ""),
        "domainType": (str, None),
        "valueType": (str, None),
        "aggregationType": (str, None),
    }


class DataSetResult(Dhis2Result):
    FIELD_SPECS = {
        "code": (str, ""),
    }

    RELATIONS = [
        Dhis2Relation(
            dhis2_field_name="dataSetElements",
            dhis2_extract_id=lambda e: e["dataElement"]["id"],
            model_name="DataElement",
            model_field="data_elements",
        ),
    ]


class IndicatorTypeResult(Dhis2Result):
    FIELD_SPECS = {
        "number": (bool, None),
        "factor": (int, None),
    }


class OrganisationUnitResult(Dhis2Result):
    FIELD_SPECS = {
        "code": (str, ""),
        "path": (str, "/"),
        "leaf": (bool, None),
    }
    RELATIONS = [
        Dhis2Relation(
            dhis2_field_name="dataSets",
            dhis2_extract_id=lambda e: e["id"],
            model_name="DataSet",
            model_field="datasets",
        ),
    ]


class IndicatorResult(Dhis2Result):
    FIELD_SPECS = {
        "code": (str, ""),
        "indicatorType": (dict, None),
        "annualized": (bool, None),
    }


class Dhis2Client:
    def __init__(self, *, url, username, password, verbose=False):
        self._api = Api(url, username, password)
        self.name = url
        self.verbose = verbose

    def fetch_info(self):
        info = self._api.get_info()
        self.name = info["systemName"]
        return info

    def fetch_data_elements(self):
        for page in self._api.get_paged(
            "dataElements", params={"fields": ":all"}, page_size=100
        ):
            if self.verbose:
                logger.info(
                    "sync_log %s: page from data_elements %s",
                    self.name,
                    page.get("pager"),
                )

            for data in page["dataElements"]:
                yield DataElementResult(data)

    def fetch_datasets(self):
        for page in self._api.get_paged(
            "dataSets", params={"fields": ":all"}, page_size=100
        ):
            if self.verbose:
                logger.info(
                    "sync_log %s: page from datasets %s", self.name, page.get("pager")
                )
            for data in page["dataSets"]:
                yield DataSetResult(data)

    def fetch_indicator_types(self):
        for page in self._api.get_paged(
            "indicatorTypes", params={"fields": ":all"}, page_size=100
        ):
            if self.verbose:
                logger.info(
                    "sync_log %s: page from indicator_types %s",
                    self.name,
                    page.get("pager"),
                )
            for data in page["indicatorTypes"]:
                yield IndicatorTypeResult(data)

    def fetch_indicators(self):
        for page in self._api.get_paged(
            "indicators", params={"fields": ":all"}, page_size=100
        ):
            if self.verbose:
                logger.info(
                    "sync_log %s: page from indicators %s", self.name, page.get("pager")
                )
            for data in page["indicators"]:
                yield IndicatorResult(data)

    def fetch_organisation_units(self):
        for page in self._api.get_paged(
            "organisationUnits", params={"fields": ":all"}, page_size=100
        ):
            if self.verbose:
                logger.info(
                    "sync_log %s: page from organisation_units %s",
                    self.name,
                    page.get("pager"),
                )
            # rewrite path -> replace "/" by "." for correct ltree path
            # warning: in place edit, can side effect on tests
            for data in page["organisationUnits"]:
                if "path" in data:
                    data["path"] = data["path"].replace("/", ".").strip(".")

                yield OrganisationUnitResult(data)
