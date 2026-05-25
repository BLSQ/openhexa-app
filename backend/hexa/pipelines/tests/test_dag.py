from django.test import SimpleTestCase

from hexa.pipelines.dag import extract_dag

LINEAR = """
from openhexa.sdk import current_run, pipeline

@pipeline("simple")
def simple():
    raw = load()
    transform(raw)
    standalone()

@simple.task
def load():
    return 1

@simple.task
def transform(x):
    return x

@simple.task
def standalone():
    return 0
"""


class ExtractDagTasksTest(SimpleTestCase):
    def test_task_nodes(self):
        dag = extract_dag(LINEAR)
        names = sorted(t["name"] for t in dag["tasks"])
        self.assertEqual(names, ["load", "standalone", "transform"])

    def test_edges_follow_data_flow(self):
        dag = extract_dag(LINEAR)
        edges = {(e["source"], e["target"]) for e in dag["edges"]}
        self.assertIn(("load", "transform"), edges)
        self.assertNotIn(("standalone", "transform"), edges)
        self.assertEqual(len(edges), 1)

    def test_nested_call_edge(self):
        source = """
from openhexa.sdk import pipeline

@pipeline("p")
def p():
    b(a())

@p.task
def a():
    return 1

@p.task
def b(x):
    return x
"""
        dag = extract_dag(source)
        edges = {(e["source"], e["target"]) for e in dag["edges"]}
        self.assertEqual(edges, {("a", "b")})

    def test_no_pipeline_returns_empty(self):
        dag = extract_dag("x = 1\n")
        self.assertEqual(dag, {"tasks": [], "edges": [], "outputs": []})

    def test_syntax_error_returns_empty(self):
        dag = extract_dag("def (:\n")
        self.assertEqual(dag, {"tasks": [], "edges": [], "outputs": []})


class ExtractDagOutputsTest(SimpleTestCase):
    SOURCE = """
from openhexa.sdk import current_run, pipeline, workspace

@pipeline("io")
def io():
    write_db()
    write_file()

@io.task
def write_db():
    current_run.add_database_output("baz")

@io.task
def write_file():
    path = f"{workspace.files_path}/transformed.csv"
    current_run.add_file_output(path)
"""

    def test_db_output_literal_name_and_task(self):
        outputs = extract_dag(self.SOURCE)["outputs"]
        db = [o for o in outputs if o["type"] == "db"]
        self.assertEqual(len(db), 1)
        self.assertEqual(db[0]["name"], "baz")
        self.assertEqual(db[0]["task_id"], "write_db")

    def test_file_output_resolves_local_fstring(self):
        outputs = extract_dag(self.SOURCE)["outputs"]
        files = [o for o in outputs if o["type"] == "file"]
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["task_id"], "write_file")
        self.assertIn("transformed.csv", files[0]["name"])

    def test_dataset_output(self):
        source = """
from openhexa.sdk import pipeline, workspace

@pipeline("d")
def d():
    make()

@d.task
def make():
    ds = workspace.create_dataset("my-dataset", "desc")
"""
        outputs = extract_dag(source)["outputs"]
        ds = [o for o in outputs if o["type"] == "dataset"]
        self.assertEqual(len(ds), 1)
        self.assertEqual(ds[0]["task_id"], "make")
        self.assertEqual(ds[0]["name"], "my-dataset")

    def test_dataset_output_deduped_and_named_by_dataset(self):
        # A task that gets-or-creates a dataset and writes a version should
        # produce exactly one dataset output, named after the dataset (not the
        # version label "latest").
        source = """
from openhexa.sdk import pipeline, workspace

@pipeline("d")
def d():
    make()

@d.task
def make():
    try:
        dataset = workspace.get_dataset("my-slug")
    except Exception:
        dataset = workspace.create_dataset("My Name", "desc")
    version = dataset.create_version("latest")
    version.add_file(buf, filename="x.csv")
"""
        outputs = extract_dag(source)["outputs"]
        ds = [o for o in outputs if o["type"] == "dataset"]
        self.assertEqual(len(ds), 1)
        self.assertEqual(ds[0]["task_id"], "make")
        self.assertEqual(ds[0]["name"], "My Name")

    def test_dataset_output_named_by_slug_when_no_create(self):
        source = """
from openhexa.sdk import pipeline, workspace

@pipeline("d")
def d():
    make()

@d.task
def make():
    dataset = workspace.get_dataset("existing-slug")
    dataset.create_version("v2")
"""
        outputs = extract_dag(source)["outputs"]
        ds = [o for o in outputs if o["type"] == "dataset"]
        self.assertEqual(len(ds), 1)
        self.assertEqual(ds[0]["name"], "existing-slug")

    def test_output_ids_are_unique(self):
        outputs = extract_dag(self.SOURCE)["outputs"]
        ids = [o["id"] for o in outputs]
        self.assertEqual(len(ids), len(set(ids)))
