from io import StringIO
from unittest.mock import patch

from django.core.exceptions import PermissionDenied
from django.core.management import call_command

from hexa.core.test import TestCase
from hexa.data_studio.models import (
    QUERY_FILE_PATH,
    SavedQuery,
    SavedQueryVersionConflict,
)
from hexa.git.exceptions import GitFileNotFound
from hexa.git.forgejo import ForgejoAPIError
from hexa.git.testutils import make_git_client_mock

from .testutils import SavedQueryTestMixin

SHA_INITIAL = "a" * 40
SHA_SECOND = "b" * 40


class SavedQueryVersioningTest(SavedQueryTestMixin, TestCase):
    """The git side of a saved query: what records a version and what does not."""

    def setUp(self):
        super().setUp()
        self.client_mock = make_git_client_mock(SHA_INITIAL)
        patcher = patch(
            "hexa.git.mixins.get_forgejo_client", return_value=self.client_mock
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_create_records_the_first_version(self):
        saved_query = self.create_saved_query(content="SELECT 1")

        self.assertEqual(SHA_INITIAL, saved_query.last_commit)
        self.assertEqual(
            f"{self.WORKSPACE.slug}-query-{saved_query.id}", saved_query.repository
        )
        self.client_mock.create_org_repository.assert_called_once()
        # Reloaded, because a version nobody can find again is not recorded.
        self.assertEqual(
            SHA_INITIAL, SavedQuery.objects.get(pk=saved_query.pk).last_commit
        )

    def test_create_commits_the_query_as_its_only_file(self):
        self.create_saved_query(content="SELECT 1")

        files = self.client_mock.commit_files.call_args.kwargs["files"]
        self.assertEqual([QUERY_FILE_PATH], [file["path"] for file in files])
        self.assertEqual("SELECT 1", files[0]["content"])

    def test_create_rolls_back_when_the_version_cannot_be_recorded(self):
        self.client_mock.create_org_repository.side_effect = ForgejoAPIError(
            "POST", "/orgs/x/repos", 500
        )

        with self.assertRaises(ForgejoAPIError):
            self.create_saved_query()

        # A saved query with no history could not be told apart from one nobody
        # ever versioned, so it must not survive the failure.
        self.assertEqual(0, SavedQuery.objects.count())

    def test_editing_the_content_records_a_version(self):
        saved_query = self.create_saved_query(content="SELECT 1")
        self.client_mock.commit_files.return_value = SHA_SECOND

        saved_query.update_if_has_perm(self.USER_EDITOR, content="SELECT 2")

        self.assertEqual(SHA_SECOND, saved_query.last_commit)
        self.assertEqual(
            SHA_SECOND, SavedQuery.objects.get(pk=saved_query.pk).last_commit
        )

    def test_the_commit_message_names_the_query(self):
        saved_query = self.create_saved_query(name="Monthly report")
        self.client_mock.commit_files.reset_mock()

        saved_query.update_if_has_perm(self.USER_EDITOR, content="SELECT 2")

        self.assertEqual(
            "Update Monthly report",
            self.client_mock.commit_files.call_args.kwargs["message"],
        )

    def test_the_commit_is_credited_to_whoever_saved(self):
        saved_query = self.create_saved_query(user=self.USER_EDITOR)
        self.client_mock.commit_files.reset_mock()

        # An admin editing a colleague's shared query is credited for that version.
        saved_query.update_if_has_perm(self.USER_ADMIN, content="SELECT 2")

        self.assertEqual(
            self.USER_ADMIN.email,
            self.client_mock.commit_files.call_args.kwargs["author_email"],
        )

    def test_renaming_records_nothing(self):
        saved_query = self.create_saved_query()
        self.client_mock.commit_files.reset_mock()

        saved_query.update_if_has_perm(self.USER_EDITOR, name="New name")

        # Only the SQL is versioned: a rename leaves the history alone.
        self.client_mock.commit_files.assert_not_called()
        self.assertEqual(SHA_INITIAL, saved_query.last_commit)

    def test_changing_the_description_records_nothing(self):
        saved_query = self.create_saved_query()
        self.client_mock.commit_files.reset_mock()

        saved_query.update_if_has_perm(self.USER_EDITOR, description="Now documented")

        self.client_mock.commit_files.assert_not_called()

    def test_resaving_identical_content_records_nothing(self):
        saved_query = self.create_saved_query(content="SELECT 1")
        self.client_mock.commit_files.reset_mock()

        saved_query.update_if_has_perm(self.USER_EDITOR, content="SELECT 1")

        self.client_mock.commit_files.assert_not_called()

    def test_content_differing_only_by_sanitized_characters_records_nothing(self):
        saved_query = self.create_saved_query(content="SELECT 1")
        self.client_mock.commit_files.reset_mock()

        # A non-breaking space becomes a plain one on the way in, so this is the
        # content already stored: a version of it would carry an empty diff.
        saved_query.update_if_has_perm(self.USER_EDITOR, content="SELECT\u00a01")

        self.client_mock.commit_files.assert_not_called()

    def test_the_recorded_version_matches_what_is_stored(self):
        saved_query = self.create_saved_query(content="SELECT 1")
        self.client_mock.commit_files.reset_mock()

        saved_query.update_if_has_perm(self.USER_EDITOR, content="SELECT 2")

        committed = self.client_mock.commit_files.call_args.kwargs["files"][0][
            "content"
        ]
        self.assertEqual(SavedQuery.objects.get(pk=saved_query.pk).content, committed)

    def test_update_rolls_back_when_the_version_cannot_be_recorded(self):
        saved_query = self.create_saved_query(content="SELECT 1")
        self.client_mock.commit_files.side_effect = ForgejoAPIError(
            "POST", "/repos/x/y/contents", 500
        )

        with self.assertRaises(ForgejoAPIError):
            saved_query.update_if_has_perm(self.USER_EDITOR, content="SELECT 2")

        # Keeping the edit would leave a change with no version to show for it.
        reloaded = SavedQuery.objects.get(pk=saved_query.pk)
        self.assertEqual("SELECT 1", reloaded.content)
        self.assertEqual(SHA_INITIAL, reloaded.last_commit)

    def test_a_refused_edit_records_nothing(self):
        saved_query = self.create_saved_query(
            user=self.USER_EDITOR, visibility="PRIVATE"
        )
        self.client_mock.commit_files.reset_mock()

        with self.assertRaises(PermissionDenied):
            saved_query.update_if_has_perm(self.USER_VIEWER, content="SELECT 2")

        self.client_mock.commit_files.assert_not_called()

    def test_deleting_archives_the_history(self):
        saved_query = self.create_saved_query()
        repository = saved_query.repository

        saved_query.delete_if_has_perm(self.USER_EDITOR)

        # Archived, not deleted: the history outlives the query.
        self.client_mock.archive_repository.assert_called_once_with(
            self.WORKSPACE.organization.slug, repository
        )

    def test_delete_rolls_back_when_the_history_cannot_be_archived(self):
        saved_query = self.create_saved_query()
        # Read before deleting: Django clears the pk of a deleted instance, and the
        # rollback this test is about does not put it back.
        pk = saved_query.pk
        self.client_mock.archive_repository.side_effect = ForgejoAPIError(
            "POST", "/repos/x/y", 500
        )

        with self.assertRaises(ForgejoAPIError):
            saved_query.delete_if_has_perm(self.USER_EDITOR)

        self.assertTrue(SavedQuery.objects.filter(pk=pk).exists())


class SavedQueryConcurrentEditTest(SavedQueryTestMixin, TestCase):
    """Editing against a version the query has moved on from."""

    def setUp(self):
        super().setUp()
        self.client_mock = make_git_client_mock(SHA_INITIAL)
        patcher = patch(
            "hexa.git.mixins.get_forgejo_client", return_value=self.client_mock
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.saved_query = self.create_saved_query(content="SELECT 1")

    def _someone_else_saves(self, content="SELECT 99"):
        """A second editor's save, landing between our load and our own save."""
        other = SavedQuery.objects.get(pk=self.saved_query.pk)
        self.client_mock.commit_files.return_value = SHA_SECOND
        other.update_if_has_perm(self.USER_ADMIN, content=content)
        self.client_mock.commit_files.reset_mock()

    def test_editing_the_version_you_read_succeeds(self):
        self.saved_query.update_if_has_perm(
            self.USER_EDITOR, content="SELECT 2", expected_version=SHA_INITIAL
        )

        self.assertEqual(
            "SELECT 2", SavedQuery.objects.get(pk=self.saved_query.pk).content
        )

    def test_editing_a_version_someone_else_replaced_is_refused(self):
        self._someone_else_saves()

        with self.assertRaises(SavedQueryVersionConflict) as raised:
            self.saved_query.update_if_has_perm(
                self.USER_EDITOR, content="SELECT 2", expected_version=SHA_INITIAL
            )

        # The version it actually collided with, so a caller can say what happened.
        self.assertEqual(SHA_SECOND, raised.exception.current_version)

    def test_a_refused_edit_writes_nothing(self):
        self._someone_else_saves(content="SELECT 99")

        with self.assertRaises(SavedQueryVersionConflict):
            self.saved_query.update_if_has_perm(
                self.USER_EDITOR, content="SELECT 2", expected_version=SHA_INITIAL
            )

        reloaded = SavedQuery.objects.get(pk=self.saved_query.pk)
        self.assertEqual("SELECT 99", reloaded.content)
        self.assertEqual(SHA_SECOND, reloaded.last_commit)
        self.client_mock.commit_files.assert_not_called()

    def test_a_rename_against_a_stale_version_is_refused_too(self):
        # The precondition is about the query, not only its SQL: a caller that sends a
        # version is asserting it read the current one.
        self._someone_else_saves()

        with self.assertRaises(SavedQueryVersionConflict):
            self.saved_query.update_if_has_perm(
                self.USER_EDITOR, name="New name", expected_version=SHA_INITIAL
            )

    def test_omitting_the_version_still_overwrites(self):
        # What a client that never read a version gets: the previous behaviour.
        self._someone_else_saves()

        self.saved_query.update_if_has_perm(self.USER_EDITOR, content="SELECT 2")

        self.assertEqual(
            "SELECT 2", SavedQuery.objects.get(pk=self.saved_query.pk).content
        )

    def test_writing_back_a_stale_copy_records_the_revert(self):
        # Without a version to check, a client saving what it loaded reverts the other
        # edit. That is a change to the query, so it has to be recorded as one rather
        # than passing for "nothing changed" because `self` still holds the old content.
        self._someone_else_saves(content="SELECT 99")

        self.saved_query.update_if_has_perm(self.USER_EDITOR, content="SELECT 1")

        reloaded = SavedQuery.objects.get(pk=self.saved_query.pk)
        self.assertEqual("SELECT 1", reloaded.content)
        self.client_mock.commit_files.assert_called_once()


class SavedQueryHistoryReadTest(SavedQueryTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client_mock = make_git_client_mock(SHA_INITIAL)
        patcher = patch(
            "hexa.git.mixins.get_forgejo_client", return_value=self.client_mock
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.saved_query = self.create_saved_query(content="SELECT 1")

    def test_get_versions_reads_the_repository_log(self):
        page = self.saved_query.get_versions(page=2, per_page=5)

        self.client_mock.get_commits.assert_called_with(
            self.WORKSPACE.organization.slug,
            self.saved_query.repository,
            page=2,
            limit=5,
        )
        self.assertEqual(2, page["page"])
        self.assertEqual([SHA_INITIAL], [item["id"] for item in page["items"]])

    def test_a_query_with_no_history_has_no_versions(self):
        # The state every query is in between the migration and the backfill.
        SavedQuery.objects.filter(pk=self.saved_query.pk).update(last_commit=None)
        self.saved_query.refresh_from_db()

        self.assertEqual(
            {"items": [], "page": 1}, self.saved_query.get_versions(page=1)
        )
        self.client_mock.get_commits.assert_not_called()

    def test_get_version_content_reads_the_query_file(self):
        self.client_mock.get_file.return_value = b"SELECT 1"

        self.assertEqual(
            "SELECT 1", self.saved_query.get_version_content(ref=SHA_INITIAL)
        )
        self.client_mock.get_file.assert_called_with(
            self.saved_query.repository,
            QUERY_FILE_PATH,
            ref=SHA_INITIAL,
            org_slug=self.WORKSPACE.organization.slug,
        )

    def test_get_version_content_propagates_an_unknown_ref(self):
        self.client_mock.get_file.side_effect = GitFileNotFound(QUERY_FILE_PATH)

        with self.assertRaises(GitFileNotFound):
            self.saved_query.get_version_content(ref="nope")

    def test_get_commit_diff_describes_the_change(self):
        self.client_mock.get_commit.return_value = {
            "id": SHA_INITIAL,
            "message": "Update Monthly report",
            "author_name": "Ada",
            "author_email": "ada@openhexa.org",
            "date": "2026-01-01T00:00:00Z",
        }
        self.client_mock.get_commit_diff.return_value = "--- a\n+++ b\n"

        diff = self.saved_query.get_commit_diff(SHA_INITIAL)

        self.assertEqual(
            {
                "id": SHA_INITIAL,
                "message": "Update Monthly report",
                "author_name": "Ada",
                "author_email": "ada@openhexa.org",
                "date": "2026-01-01T00:00:00Z",
                "raw_diff": "--- a\n+++ b\n",
            },
            diff,
        )


class BackfillSavedQueryRepositoriesTest(SavedQueryTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client_mock = make_git_client_mock(SHA_INITIAL)
        patcher = patch(
            "hexa.git.mixins.get_forgejo_client", return_value=self.client_mock
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def _query_without_history(self, **kwargs):
        """A saved query in the state the migration leaves existing ones in."""
        saved_query = self.create_saved_query(**kwargs)
        SavedQuery.objects.filter(pk=saved_query.pk).update(last_commit=None)
        self.client_mock.reset_mock()
        return SavedQuery.objects.get(pk=saved_query.pk)

    def test_records_a_first_version_for_a_query_that_has_none(self):
        saved_query = self._query_without_history(content="SELECT 1")

        call_command("backfill_saved_query_repositories")

        saved_query.refresh_from_db()
        self.assertEqual(SHA_INITIAL, saved_query.last_commit)
        files = self.client_mock.commit_files.call_args.kwargs["files"]
        self.assertEqual("SELECT 1", files[0]["content"])

    def test_keeps_the_repository_name_the_migration_assigned(self):
        saved_query = self._query_without_history()
        expected = saved_query.repository

        call_command("backfill_saved_query_repositories")

        saved_query.refresh_from_db()
        self.assertEqual(expected, saved_query.repository)

    def test_re_running_records_nothing_more(self):
        self._query_without_history()
        call_command("backfill_saved_query_repositories")
        self.client_mock.reset_mock()

        call_command("backfill_saved_query_repositories")

        self.client_mock.create_org_repository.assert_not_called()
        self.client_mock.commit_files.assert_not_called()

    def test_a_failure_leaves_the_other_queries_to_be_done(self):
        first = self._query_without_history(name="First")
        second = self._query_without_history(name="Second")
        # Whichever comes first fails; the run must not stop there.
        self.client_mock.create_org_repository.side_effect = [
            ForgejoAPIError("POST", "/orgs/x/repos", 500),
            {},
        ]

        call_command("backfill_saved_query_repositories")

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual({None, SHA_INITIAL}, {first.last_commit, second.last_commit})

    def test_an_authorless_query_is_credited_to_the_instance(self):
        saved_query = self._query_without_history()
        SavedQuery.objects.filter(pk=saved_query.pk).update(created_by=None)

        call_command("backfill_saved_query_repositories")

        self.assertEqual(
            SHA_INITIAL, SavedQuery.objects.get(pk=saved_query.pk).last_commit
        )

    def test_check_records_nothing(self):
        self._query_without_history()

        call_command("backfill_saved_query_repositories", "--check")

        self.client_mock.create_org_repository.assert_not_called()
        self.client_mock.commit_files.assert_not_called()

    def test_check_reports_content_that_no_longer_matches_its_version(self):
        saved_query = self.create_saved_query(content="SELECT 1")
        self.client_mock.get_file.return_value = b"SELECT 2"
        out = StringIO()

        call_command("backfill_saved_query_repositories", "--check", stdout=out)

        self.assertIn("drifted", out.getvalue())
        self.assertIn(saved_query.slug, out.getvalue())

    def test_check_reports_a_query_with_no_version(self):
        saved_query = self._query_without_history()
        out = StringIO()

        call_command("backfill_saved_query_repositories", "--check", stdout=out)

        self.assertIn("no version", out.getvalue())
        self.assertIn(saved_query.slug, out.getvalue())
