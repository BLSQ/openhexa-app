from unittest.mock import NonCallableMagicMock, create_autospec

from hexa.git.client import GitClient

# Shaped like a real sha because it is stored: `SavedQuery.last_commit` and
# `GitWebapp.published_commit` are CharFields, which a bare mock cannot be written to,
# and a sha-looking value keeps assertion failures readable.
FAKE_COMMIT_SHA = "0" * 40


def make_git_client_mock(sha: str = FAKE_COMMIT_SHA) -> NonCallableMagicMock:
    """A stand-in for the git client, answering with storable, correctly shaped values.

    Specced against `GitClient` rather than left open, so a test stubbing a method the
    interface does not have — a typo, or one that was renamed since — fails instead of
    quietly configuring an attribute nothing will ever call.

    Return type is the mock, not `GitClient`: callers use it in both roles, passing it
    where a client is expected *and* configuring and asserting on it
    (`commit_files.return_value`, `side_effect`, `assert_called_once`). The mock type
    admits both; `GitClient` would only describe the half that has no methods for
    setting up a test.

    Defaults cover the calls whose result a model keeps or iterates over — the ones a
    bare mock breaks. Tests that care about a specific answer set it themselves.
    """
    client = create_autospec(GitClient, instance=True)
    client.commit_files.return_value = sha
    client.get_commits.return_value = [
        {
            "id": sha,
            "message": "Initial content",
            "author_name": "Test",
            "author_email": "test@openhexa.org",
            "date": "2020-01-01T00:00:00Z",
        }
    ]
    client.commit_exists.return_value = True
    client.get_file.return_value = b""
    client.get_repository_files.return_value = []
    client.get_files_tree.return_value = []
    client.list_org_repositories.return_value = []
    return client
