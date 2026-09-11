import io
from zipfile import ZipFile

from hexa.core.test import TestCase
from hexa.pipelines.dag import extract_dag, extract_dag_from_zipfile

# Fixtures below are trimmed from real pipelines: the SDK's CLI scaffold and example
# pipelines, plus two pipelines written by users. They are the shapes the extractor
# actually meets in production.

SCAFFOLD = '''
"""Template for newly generated pipelines."""

from openhexa.sdk import current_run, pipeline


@pipeline("my-pipeline")
def my_pipeline():
    """Write your pipeline orchestration here."""
    count = task_1()
    task_2(count)


@my_pipeline.task
def task_1():
    return 42


@my_pipeline.task
def task_2(count):
    current_run.log_info(f"count is {count}")


if __name__ == "__main__":
    my_pipeline()
'''

BRANCH_AND_MERGE = """
from openhexa.sdk import parameter, pipeline


@pipeline("Logistic stats", "Test")
@parameter("deg", type=str)
@parameter("periods", type=str, multiple=True)
@parameter("oul", type=int, default=2)
def logistic_stats(deg: str, periods: str, oul: int):
    dhis2_data = dhis2_download(deg, periods, oul)
    gadm_data = gadm_download()
    worldpop_data = worldpop_download()

    model(dhis2_data, gadm_data, worldpop_data)


@logistic_stats.task
def dhis2_download(data_element_group: str, periods: str, org_unit_level: int):
    return {}


@logistic_stats.task
def gadm_download():
    return b""


@logistic_stats.task
def worldpop_download():
    return b""


@logistic_stats.task
def model(dhis2_data, gadm_data, worldpop_data):
    pass
"""

DISCONNECTED = """
from openhexa.sdk import pipeline


@pipeline("Simple IO")
def simple_io():
    raw_files_data = load_files_data()
    transform_and_write_files_data(raw_files_data)

    raw_sql_data = load_data_from_postgresql()
    transform_and_write_sql_data(raw_sql_data)

    load_dhis2_data()


@simple_io.task
def load_files_data():
    pass


@simple_io.task
def transform_and_write_files_data(raw_data):
    pass


@simple_io.task
def load_data_from_postgresql():
    pass


@simple_io.task
def transform_and_write_sql_data(raw_data):
    pass


@simple_io.task
def load_dhis2_data():
    pass
"""

DIAMOND = '''
import pandas as pd
import requests
from openhexa.sdk.pipelines import current_run, pipeline
from openhexa.sdk.workspaces import workspace


def fetch_history(device_id, start_date, end_date):
    """Module-level helper, not a task: it must never become a node."""
    return pd.read_csv(requests.get(device_id).content)


@pipeline("brussels_bikes", name="Bikes in Brussels")
def bikes():
    current_run.log_info("Starting pipeline...")
    devices = load_devices()
    history = load_history(devices)

    save_dataset(devices, history)


@bikes.task
def save_dataset(devices, history):
    workspace.get_dataset("bikes-in-brussels")


@bikes.task
def load_history(devices):
    history = []
    for row in devices.itertuples():
        history.append(fetch_history(row.id, None, None))
    return history


@bikes.task
def load_devices():
    return requests.get("https://example.org").json()


if __name__ == "__main__":
    bikes()
'''

SINGLE_TASK = '''
from openhexa.sdk.pipelines import current_run, parameter, pipeline, task
from openhexa.sdk.workspaces.connection import DHIS2Connection


@pipeline("dhis2-tracker-programs")
@parameter("dhis2_connection", type=DHIS2Connection, required=True)
def dhis2_tracker_programs(dhis2_connection):
    """Pipeline qui affiche les programmes Tracker d'une instance DHIS2."""
    fetch_and_display_tracker_programs(dhis2_connection)


@dhis2_tracker_programs.task
def fetch_and_display_tracker_programs(dhis2_connection: DHIS2Connection):
    current_run.log_info("Recuperation des programmes Tracker...")


if __name__ == "__main__":
    dhis2_tracker_programs()
'''


class ExtractDagTest(TestCase):
    def assertGraph(self, source, tasks, edges):
        dag = extract_dag(source)
        self.assertEqual([task["id"] for task in dag["tasks"]], tasks)
        self.assertEqual(
            [(edge["source"], edge["target"]) for edge in dag["edges"]], edges
        )
        for task in dag["tasks"]:
            self.assertEqual(task["id"], task["name"])

    def test_linear_chain(self):
        """The CLI scaffold every new pipeline starts from."""
        self.assertGraph(SCAFFOLD, ["task_1", "task_2"], [("task_1", "task_2")])

    def test_branch_and_merge(self):
        """Three independent producers feeding one consumer, plus parameter edges.

        The parameter codes come from the pipeline function's own signature (deg, periods,
        oul), never from the task's signature (data_element_group, periods, org_unit_level).
        """
        self.assertGraph(
            BRANCH_AND_MERGE,
            ["dhis2_download", "gadm_download", "worldpop_download", "model"],
            [
                ("deg", "dhis2_download"),
                ("periods", "dhis2_download"),
                ("oul", "dhis2_download"),
                ("dhis2_download", "model"),
                ("gadm_download", "model"),
                ("worldpop_download", "model"),
            ],
        )

    def test_disconnected_components(self):
        """Two independent chains and an isolated task: the graph is a forest."""
        self.assertGraph(
            DISCONNECTED,
            [
                "load_files_data",
                "transform_and_write_files_data",
                "load_data_from_postgresql",
                "transform_and_write_sql_data",
                "load_dhis2_data",
            ],
            [
                ("load_files_data", "transform_and_write_files_data"),
                ("load_data_from_postgresql", "transform_and_write_sql_data"),
            ],
        )

    def test_diamond(self):
        """One producer feeding two consumers, one of which also feeds the other.

        Tasks are declared in reverse execution order here, so the returned order is
        declaration order and carries no meaning — layout must come from the edges.
        """
        self.assertGraph(
            DIAMOND,
            ["save_dataset", "load_history", "load_devices"],
            [
                ("load_devices", "load_history"),
                ("load_devices", "save_dataset"),
                ("load_history", "save_dataset"),
            ],
        )

    def test_single_task_with_parameter(self):
        self.assertGraph(
            SINGLE_TASK,
            ["fetch_and_display_tracker_programs"],
            [("dhis2_connection", "fetch_and_display_tracker_programs")],
        )

    def test_ignores_undecorated_helper(self):
        """fetch_history looks like a task but carries no decorator."""
        self.assertNotIn(
            "fetch_history", [task["id"] for task in extract_dag(DIAMOND)["tasks"]]
        )

    def test_ignores_non_task_calls_in_body(self):
        """current_run.log_info() sits in the body of DIAMOND and is not a task."""
        for edge in extract_dag(DIAMOND)["edges"]:
            self.assertNotIn("log_info", edge)

    def test_ignores_bare_task_import(self):
        """SINGLE_TASK imports a bare `task` name that is never used as a decorator."""
        self.assertEqual(len(extract_dag(SINGLE_TASK)["tasks"]), 1)

    def test_nested_task_call(self):
        source = """
from openhexa.sdk import pipeline


@pipeline("nested")
def nested():
    t3(t2(t1()))


@nested.task
def t1():
    pass


@nested.task
def t2(value):
    pass


@nested.task
def t3(value):
    pass
"""
        # t1 feeds t2, not t3: at runtime it is t2 that holds the reference to t1.
        self.assertGraph(source, ["t1", "t2", "t3"], [("t1", "t2"), ("t2", "t3")])

    def test_task_called_twice_is_one_node(self):
        """A node is a task definition, not an invocation."""
        source = """
from openhexa.sdk import pipeline


@pipeline("repeated")
def repeated():
    a = fetch()
    b = fetch()
    join(a, b)


@repeated.task
def fetch():
    pass


@repeated.task
def join(first, second):
    pass
"""
        self.assertGraph(source, ["fetch", "join"], [("fetch", "join")])

    def test_loop_in_body_yields_single_node(self):
        """The iteration count is unknowable statically, so a loop is still one node."""
        source = """
from openhexa.sdk import parameter, pipeline


@pipeline("looping")
@parameter("countries", type=str, multiple=True)
def looping(countries):
    for country in countries:
        fetch(country)


@looping.task
def fetch(country):
    pass
"""
        self.assertGraph(source, ["fetch"], [])

    def test_pipeline_without_tasks(self):
        """No node is synthesized: the caller renders nothing rather than invented code."""
        source = """
from openhexa.sdk import parameter, pipeline


@pipeline("empty")
@parameter("foo", type=str)
def empty(foo):
    print(foo)
"""
        self.assertGraph(source, [], [])

    def test_module_without_pipeline(self):
        self.assertGraph("import os\n\n\ndef main():\n    pass\n", [], [])

    def test_syntax_error(self):
        self.assertGraph("def broken(:\n", [], [])

    def test_empty_source(self):
        self.assertGraph("", [], [])


class ExtractDagFromZipfileTest(TestCase):
    def build_zipfile(self, files: dict) -> bytes:
        buffer = io.BytesIO()
        with ZipFile(buffer, "w") as zip_file:
            for path, content in files.items():
                zip_file.writestr(path, content)
        return buffer.getvalue()

    def test_reads_entrypoint(self):
        dag = extract_dag_from_zipfile(self.build_zipfile({"pipeline.py": SCAFFOLD}))
        self.assertEqual([task["id"] for task in dag["tasks"]], ["task_1", "task_2"])

    def test_ignores_other_modules(self):
        """Only pipeline.py is read: another module's @pipeline must not be described."""
        dag = extract_dag_from_zipfile(
            self.build_zipfile({"pipeline.py": SCAFFOLD, "backup/old.py": DIAMOND})
        )
        self.assertEqual([task["id"] for task in dag["tasks"]], ["task_1", "task_2"])

    def test_missing_entrypoint(self):
        dag = extract_dag_from_zipfile(self.build_zipfile({"notebook.ipynb": "{}"}))
        self.assertEqual(dag, {"tasks": [], "edges": []})

    def test_not_a_zipfile(self):
        self.assertEqual(
            extract_dag_from_zipfile(b"not a zip"), {"tasks": [], "edges": []}
        )

    def test_no_zipfile(self):
        """Notebook versions carry no archive."""
        self.assertEqual(extract_dag_from_zipfile(None), {"tasks": [], "edges": []})
