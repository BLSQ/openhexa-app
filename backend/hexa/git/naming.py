import hashlib

# Forgejo rejects a repository name longer than this.
REPO_NAME_MAX_LENGTH = 100


def build_repo_name(readable: str) -> str:
    """Make a name Forgejo accepts.

    A repository is named after the slugs of the object. As we have a length
    limit, we cut off part of it; and replace the last bits with a hash to ensure
    no duplicated repo names.
    """
    if len(readable) <= REPO_NAME_MAX_LENGTH:
        return readable

    digest = hashlib.sha1(readable.encode()).hexdigest()[:8]
    return f"{readable[: REPO_NAME_MAX_LENGTH - len(digest) - 1]}-{digest}"
