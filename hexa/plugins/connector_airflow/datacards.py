from django.templatetags.static import static
from django.utils.translation import ugettext_lazy as _

from hexa.catalog.datacards import OpenHexaMetaDataSection
from hexa.ui.datacard import (
    Datacard,
    Section,
    TextProperty,
    URLProperty,
    DateProperty,
)


class ClusterSection(Section):
    title = "Airflow Data"

    name = TextProperty(text="name")
    url = URLProperty(url="web_url")


class ClusterCard(Datacard):
    title = "name"
    subtitle = "generic_description"
    image_src = "_image_src"

    external = ClusterSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self) -> str:
        return _("Airflow Cluster")

    @property
    def _image_src(self) -> str:
        return static("connector_airflow/img/symbol.svg")


class DagSection(Section):
    title = "Airflow Data"

    dag_id = TextProperty(text="dag_id", label="Identifier")
    description = TextProperty(text="description")


class DagCard(Datacard):
    title = "dag_id"
    subtitle = "generic_description"
    image_src = "_image_src"

    external = DagSection()
    metadata = OpenHexaMetaDataSection(value="index")

    @property
    def generic_description(self) -> str:
        return _("Airflow DAG")

    @property
    def _image_src(self) -> str:
        return static("connector_airflow/img/symbol.svg")


class DagRunSection(Section):
    title = "Airflow Data"

    run_id = TextProperty(text="run_id", label="Identifier")
    message = TextProperty(text="message")
    execution_date = DateProperty(date="execution_date")
    state = TextProperty(text="state")
    dag_config = TextProperty(text="dag_config", label="Configuration")


class DagRunCard(Datacard):
    title = "dag_id"
    subtitle = "generic_description"
    image_src = "_image_src"

    external = DagRunSection()

    @property
    def generic_description(self) -> str:
        return _("Airflow DAG run")

    @property
    def _image_src(self) -> str:
        return static("connector_airflow/img/symbol.svg")
