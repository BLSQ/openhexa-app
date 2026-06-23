class GitError(Exception):
    """Base class for errors raised by the git client layer.

    Lets callers handle git failures without depending on a specific backend
    (e.g. Forgejo) or on transport details such as HTTP status codes.
    """


class GitFileNotFound(GitError):
    """A requested file path does not exist in the repository."""
