from hexa.ui import datacard


class OpenHexaMetaDataSection(
    datacard.Section
):  # TODO: duplicated: move in catalog module
    title = "OpenHexa Metadata"

    id = datacard.HiddenProperty(value="only_index.id")
    owner = datacard.URLProperty(
        url="only_index.owner.url", text="only_index.owner.name"
    )
    label = datacard.TextProperty(text="only_index.label", editable=True)
    tags = datacard.TagProperty(tags="only_index.tags.all")
    location = datacard.CountryProperty(countries="only_index.countries")
    description = datacard.TextProperty(text="only_index.description", markdown=True)
    last_synced_at = datacard.DateProperty(
        label="Last synced at",
        date="only_index.last_synced_at",
        date_format="timesince",
    )
