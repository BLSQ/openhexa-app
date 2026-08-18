from django.test import TransactionTestCase

from hexa.core.test.migrator import Migrator
from hexa.workspaces.tests.testutils import create_workspace


class Migration0006Test(TransactionTestCase):
    """The backfill runs against rows that predate the slug column, where names
    are free to repeat inside a workspace.

    ``TransactionTestCase``: the migration adds a column, and PostgreSQL refuses
    to ALTER a table that has pending trigger events from inserts made in the
    same transaction.
    """

    migrate_from = ("data_studio", "0005_savedquery_visibility_and_more")
    migrate_to = ("data_studio", "0006_savedquery_slug")

    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate(*self.migrate_from)

    def tearDown(self):
        # Leave the schema where the rest of the suite expects it, including
        # when a test failed before migrating forward itself.
        self.migrator.migrate(*self.migrate_to)

    def _create_workspace(self, slug):
        # `slug` and `db_name` are only filled in by create_if_has_perm, which
        # provisions a real database; both are unique, so the plain create path
        # needs them spelled out or a second workspace collides on the empty one.
        return create_workspace(name=slug, slug=slug, db_name=slug)

    def _create_saved_query(self, workspace, name):
        # Only data_studio is rolled back, so workspaces are created through the
        # real model while saved queries need the historical one (theirs has no
        # slug field yet, and the column does not exist).
        SavedQuery = self.migrator.apps.get_model("data_studio", "SavedQuery")
        return SavedQuery.objects.create(
            workspace_id=workspace.id, name=name, content="SELECT 1"
        )

    def _slug_of(self, saved_query):
        SavedQuery = self.migrator.apps.get_model("data_studio", "SavedQuery")
        return SavedQuery.objects.get(pk=saved_query.pk).slug

    def test_backfills_slug_from_name(self):
        query = self._create_saved_query(self._create_workspace("ws"), "My query")

        self.migrator.migrate(*self.migrate_to)

        self.assertEqual("my-query", self._slug_of(query))

    def test_backfills_duplicate_names_to_distinct_slugs(self):
        workspace = self._create_workspace("ws")
        queries = [self._create_saved_query(workspace, "My query") for _ in range(3)]

        self.migrator.migrate(*self.migrate_to)

        slugs = [self._slug_of(query) for query in queries]
        self.assertEqual(3, len(set(slugs)))
        self.assertIn("my-query", slugs)
        self.assertTrue(all(slug.startswith("my-query") for slug in slugs))

    def test_backfills_same_name_in_two_workspaces_to_same_slug(self):
        first = self._create_saved_query(self._create_workspace("ws-1"), "My query")
        second = self._create_saved_query(self._create_workspace("ws-2"), "My query")

        self.migrator.migrate(*self.migrate_to)

        self.assertEqual("my-query", self._slug_of(first))
        self.assertEqual("my-query", self._slug_of(second))

    def test_backfills_unslugifiable_name(self):
        query = self._create_saved_query(self._create_workspace("ws"), "!@#$%")

        self.migrator.migrate(*self.migrate_to)

        self.assertEqual("query", self._slug_of(query))
