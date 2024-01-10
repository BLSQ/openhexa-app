from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hexa.catalog.datacards import OpenHEXAMetaDataSection
from hexa.plugins.connector_postgresql.models import Database, Table
from hexa.ui.datacard import CodeProperty, Datacard, Section, TextProperty


class DatabaseSection(Section):
    title = "PostgreSQL Data"

    hostname = TextProperty(text="hostname", translate=False)
    database = TextProperty(text="database", translate=False)
    username = TextProperty(text="username", translate=False)
    url = TextProperty(text="url", translate=False, secret=True)


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

engine = create_engine(os.environ["POSTGRESQL_{{ label }}_URL"])

# Create sample dataframe
df = pd.DataFrame({"name": ["Jane", "John", "Tyler"], "age": [19, 17, 22]})

# Write data
df.to_sql("database_tutorial", con=engine, if_exists="replace")

# Read data
pd.read_sql("SELECT * FROM database_tutorial", con=engine)
            """.replace(
            "{{ label }}", item.unique_name.replace("-", "_").upper()
        )

    def get_r_usage(self, item: Database):
        return """
library(DBI)

con <- dbConnect(
    RPostgres::Postgres(),
    dbname = Sys.getenv("POSTGRESQL_{{ label }}_DATABASE"),
    host = Sys.getenv("POSTGRESQL_{{ label }}_HOSTNAME"),
    port = Sys.getenv("POSTGRESQL_{{ label }}_PORT"),
    user = Sys.getenv("POSTGRESQL_{{ label }}_USERNAME"),
    password = Sys.getenv("POSTGRESQL_{{ label }}_PASSWORD")
)

dbWriteTable(con, "some_table_name", Data_fin, overwrite=TRUE)
            """.replace(
            "{{ label }}", item.unique_name.replace("-", "_").upper()
        )


class DatabaseCard(Datacard):
    title = "display_name"
    subtitle = "generic_description"
    image_src = "postgres_image_src"
    # actions = [Action(label="Sync", url="get_sync_url", icon="refresh")]

    external = DatabaseSection()
    metadata = OpenHEXAMetaDataSection(value="index")
    usage = UsageSection()

    @property
    def generic_description(self):
        return _("PostgreSQL Database")

    @property
    def postgres_image_src(self):
        return static("connector_postgresql/img/symbol.svg")

    def get_sync_url(self, database: Database):
        return reverse(
            "catalog:datasource_sync",
            kwargs={
                "datasource_id": database.id,
                "datasource_contenttype_id": ContentType.objects.get_for_model(
                    Database
                ).id,
            },
        )


class TableSection(Section):
    title = "PostgreSQL Data"

    name = TextProperty(text="name", translate=False)
    rows = TextProperty(text="get_rows", label=_("Row count"), translate=False)

    def get_rows(self, table: Table):
        return f"{table.rows}"


class TableCard(Datacard):
    title = "name"
    subtitle = "generic_description"
    image_src = "postgres_image_src"

    external = TableSection()
    metadata = OpenHEXAMetaDataSection(value="index")

    @property
    def generic_description(self):
        return _("PostgreSQL Table")

    @property
    def postgres_image_src(self):
        return static("connector_postgresql/img/symbol.svg")
