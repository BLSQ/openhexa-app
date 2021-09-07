from hexa.catalog.models import Index
from hexa.ui import datacard


class OpenHexaMetaDataSection(datacard.Section):
    title = "OpenHexa Metadata"

    owner = datacard.URLProperty(url="only_index.owner.url", text="owner.name")
    label = datacard.TextProperty(text="label", editable=True)
    tags = datacard.TagProperty(tags="tags.all", editable=True)
    countries = datacard.CountryProperty(value="countries", editable=True)
    description = datacard.TextProperty(
        text="description", markdown=True, editable=True
    )
    last_synced_at = datacard.DateProperty(
        label="Last synced at",
        date="last_synced_at",
        date_format="timesince",
    )

    class Meta:
        model = Index
