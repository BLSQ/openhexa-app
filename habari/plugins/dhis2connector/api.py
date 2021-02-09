from dhis2 import Api


class Dhis2Item:
    """Wrapper class for DHIS2 result items"""

    def __init__(self, data):
        self._data = data

    def __getitem__(self, item):
        if item == "description":
            return self._extract_description("en")

        return self._data.get(item, "")

    def _extract_description(self, locale):
        try:
            # Attempt to extract the description for the provided locale (which can be None)
            return next(
                p
                for p in self._data["translations"]
                # If locale is None, the first description will be returned
                if p["property"] == "DESCRIPTION"
                and (locale is None or locale in p["locale"])
            )["value"]
        except StopIteration:
            if (
                locale is None
            ):  # Locale is None: if no description at all, return an empty string
                return ""

            # Could not find a description for the provided locale, find any description
            return self._extract_description(None)


class Dhis2Client:
    def __init__(self, *, url, username, password):
        self._api = Api(url, username, password)

    def fetch_data_elements(self):
        return [
            Dhis2Item(data)
            for data in self._api.get_paged(
                "dataElements", params={"fields": ":all"}, page_size=100, merge=True
            )["dataElements"]
        ]

    def fetch_indicators(self):
        return [
            Dhis2Item(data)
            for data in self._api.get_paged(
                "indicators", params={"fields": ":all"}, page_size=100, merge=True
            )["indicators"]
        ]
