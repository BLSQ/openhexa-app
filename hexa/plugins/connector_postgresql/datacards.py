from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from hexa.plugins.connector_postgresql.models import Database
from hexa.ui.datacard import (
    Datacard,
    Section,
    TextProperty,
    URLProperty,
    DateProperty,
    TagProperty,
    CountryProperty,
    Action,
    BooleanProperty,
    CodeProperty,
)


class OpenHexaMetaDataSection(Section):  # TODO: duplicated: move in catalog module
    title = "OpenHexa Metadata"

    owner = URLProperty(url="only_index.owner.url", text="only_index.owner.name")
    label = TextProperty(text="only_index.label")
    tags = TagProperty(tags="only_index.tags.all")
    location = CountryProperty(countries="only_index.countries")
    description = TextProperty(text="only_index.description", markdown=True)
    last_synced_at = DateProperty(
        label="Last synced at",
        date="only_index.last_synced_at",
        date_format="timesince",
    )


class DatabaseSection(Section):
    title = "PostgreSQL Data"

    hostname = TextProperty(text="hostname")
    database = TextProperty(text="database")
    username = TextProperty(text="username")
    url = TextProperty(text="url")


class UsageSection(Section):
    title = "Code samples"

    usage_python = CodeProperty(
        label="Usage in Python", code="get_python_usage", language="python"
    )
    usage_r = CodeProperty(label="Usage in R", code="get_r_usage", language="r")

    def get_python_usage(self, item: Database):
        return """
import os
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(os.environ["{{ datasource.env_name }}_URL"])

# create sample dataframe
df = pd.DataFrame({"name": ["Jane", "John", "Tyler"], "age": [19, 17, 22]})

# Write data
df.to_sql("database_tutorial", con=engine, if_exists="replace")
            """.replace(
            "{{ datasource.env_name }}", item.env_name
        )

    def get_r_usage(self, item: Database):
        return """
library(DBI)

con <- dbConnect(
    RPostgres::Postgres(),
    dbname = Sys.getenv("{{ datasource.env_name }}_DATABASE"),
    host = Sys.getenv("{{ datasource.env_name }}_HOSTNAME"),
    port = Sys.getenv("{{ datasource.env_name }}_PORT"),
    user = Sys.getenv("{{ datasource.env_name }}_USERNAME"),
    password = Sys.getenv("{{ datasource.env_name }}_PASSWORD")
)

dbWriteTable(con, "some_table_name", Data_fin, overwrite=TRUE)
            """.replace(
            "{{ datasource.env_name }}", item.env_name
        )


class DatabaseCard(Datacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "postgres_image_src"
    actions = [Action(label="Sync", url="get_sync_url", icon="refresh")]

    external = DatabaseSection()
    metadata = OpenHexaMetaDataSection()
    usage = UsageSection()

    @property
    def generic_description(self):
        return _("DHIS2 Instance")

    @property
    def postgres_image_src(self):
        return static("connector_postgresql/img/symbol.svg")

    def get_sync_url(self, database: Database):
        return reverse(
            "connector_postgresql:datasource_sync",
            kwargs={"datasource_id": database.id},
        )
