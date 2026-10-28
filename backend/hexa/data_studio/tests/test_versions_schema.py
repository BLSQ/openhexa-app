from unittest.mock import patch

from hexa.core.test import GraphQLTestCase
from hexa.git.exceptions import GitFileNotFound
from hexa.git.forgejo import ForgejoAPIError
from hexa.git.testutils import make_git_client_mock

from .testutils import SavedQueryTestMixin

SHA = "c" * 40

VERSIONS_QUERY = """
  query ($slug: String!, $ref: String!) {
    savedQueryBySlug(slug: $slug) {
      versions(page: 1, perPage: 5) {
        page
        items { id message authorName authorEmail date }
      }
      commitDiff(ref: $ref) { id message rawDiff }
      versionContent(ref: $ref)
    }
  }
"""


class SavedQueryVersionsSchemaTest(SavedQueryTestMixin, GraphQLTestCase):
    """The history of a saved query, read through GraphQL."""

    def setUp(self):
        super().setUp()
        self.client_mock = make_git_client_mock(SHA)
        patcher = patch(
            "hexa.git.mixins.get_forgejo_client", return_value=self.client_mock
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.saved_query = self.create_saved_query(content="SELECT 1")
        self.client.force_login(self.USER_EDITOR)

    def _query(self, ref=SHA):
        return self.run_query(
            VERSIONS_QUERY, {"slug": self.saved_query.slug, "ref": ref}
        )["data"]["savedQueryBySlug"]

    def test_versions_list_the_commits(self):
        self.client_mock.get_commit_diff.return_value = "diff --git a/query.sql"
        self.client_mock.get_file.return_value = b"SELECT 1"

        data = self._query()

        self.assertEqual(1, data["versions"]["page"])
        self.assertEqual(
            [
                {
                    "id": SHA,
                    "message": "Initial content",
                    "authorName": "Test",
                    "authorEmail": "test@openhexa.org",
                    "date": "2020-01-01T00:00:00Z",
                }
            ],
            data["versions"]["items"],
        )
        self.assertEqual(
            {
                "id": SHA,
                "message": "Initial content",
                "rawDiff": "diff --git a/query.sql",
            },
            data["commitDiff"],
        )
        self.assertEqual("SELECT 1", data["versionContent"])

    def test_unknown_ref_reads_as_null(self):
        self.client_mock.get_file.side_effect = GitFileNotFound("query.sql")
        self.client_mock.get_commit.side_effect = ForgejoAPIError("GET", "/commit", 404)

        data = self._query(ref="unknown")

        self.assertIsNone(data["versionContent"])
        self.assertIsNone(data["commitDiff"])

    def test_history_unavailable_reads_as_empty(self):
        # The query itself stays readable when the git server is down: content
        # is the source of truth, history is a bonus.
        self.client_mock.get_commits.side_effect = ForgejoAPIError("GET", "/repo", 502)
        self.client_mock.get_commit.side_effect = ForgejoAPIError("GET", "/repo", 502)
        self.client_mock.get_file.side_effect = ForgejoAPIError("GET", "/repo", 502)

        data = self._query()

        self.assertEqual({"page": 1, "items": []}, data["versions"])
        self.assertIsNone(data["commitDiff"])
        self.assertIsNone(data["versionContent"])

    def test_query_without_repository_has_no_history(self):
        self.saved_query.repository = None
        self.saved_query.save()

        data = self._query()

        self.assertEqual([], data["versions"]["items"])
        self.assertIsNone(data["commitDiff"])
        self.assertIsNone(data["versionContent"])
