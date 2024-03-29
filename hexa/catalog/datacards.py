from hexa.catalog.models import Index
from hexa.ui import datacard


class OpenHEXAMetaDataSection(datacard.Section):
    title = "OpenHEXA Metadata"
    owner = datacard.OwnerProperty(url="owner.url", text="owner.name", editable=True)
    label = datacard.TextProperty(text="label", editable=True)
    tags = datacard.TagProperty(value="tags.all", editable=True)
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
