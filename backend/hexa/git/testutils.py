from unittest.mock import NonCallableMagicMock, create_autospec

from hexa.git.client import GitClient

# Shaped like a real sha because it is stored in a CharField, which a bare mock
# cannot be written to.
FAKE_COMMIT_SHA = "0" * 40


def make_git_client_mock(sha: str = FAKE_COMMIT_SHA) -> NonCallableMagicMock:
    """A stand-in for the git client, answering with storable, correctly shaped values.

    Specced against `GitClient`, so stubbing a method the interface does not have fails
    instead of quietly configuring an attribute nothing calls. Typed as the mock rather
    than `GitClient` because callers also configure and assert on it.

    Defaults cover the calls whose result a model keeps or iterates over — the ones a
    bare mock breaks. Tests wanting a specific answer set it themselves.
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
    client.get_commit.return_value = {
        "id": sha,
        "message": "Initial content",
        "author_name": "Test",
        "author_email": "test@openhexa.org",
        "date": "2020-01-01T00:00:00Z",
    }
    client.commit_exists.return_value = True
    client.get_file.return_value = b""
    client.get_repository_files.return_value = []
    client.get_files_tree.return_value = []
    client.list_org_repositories.return_value = []
    return client
