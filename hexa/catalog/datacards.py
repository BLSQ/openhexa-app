from hexa.catalog.models import Index
from hexa.ui import datacard


class OpenHexaMetaDataSection(datacard.Section):
    title = "OpenHexa Metadata"

    owner = datacard.URLProperty(url="only_index.owner.url", text="owner.name")
    label = datacard.TextProperty(text="label", editable=True)
    tags = datacard.TagProperty(tags="tags.all")
    location = datacard.CountryProperty(countries="countries")
    description = datacard.TextProperty(text="description", markdown=True)
    last_synced_at = datacard.DateProperty(
        label="Last synced at",
        date="last_synced_at",
        date_format="timesince",
    )

    class Meta:
        model = Index
