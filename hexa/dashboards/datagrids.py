import urllib.parse

from django.urls import reverse

from hexa.ui.datagrid import CountryColumn, Datagrid, LeadingColumn, LinkColumn

from .models import Index


class DashboardGrid(Datagrid):
    lead = LeadingColumn(
        label="All dashboards",
        text="label",
        secondary_text="content",
        image_src="screenshot",
        detail_url="get_dashboard_url",
    )
    location = CountryColumn(value="countries")
    info = LinkColumn(text="Info", url="info_dashboard_url")

    def screenshot(self, index: Index):
        return reverse(
            "dashboards:dashboard_image", kwargs={"dashboard_id": index.object.id}
        )

    def get_dashboard_url(self, index: Index):
        return (
            reverse("metrics:save_redirect")
            + "?to="
            + urllib.parse.quote(index.object.url, safe="")
        )

    def info_dashboard_url(self, index: Index):
        return reverse(
            "dashboards:dashboard_detail", kwargs={"dashboard_id": index.object.id}
        )
