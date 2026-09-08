# Forgejo rejects a repository name longer than this.
REPO_NAME_MAX_LENGTH = 100


def build_repo_name(readable: str, *, unique: str) -> str:
    """Compose a repository name that fits Forgejo's limit and stays unique whatever it costs.

    `readable` is for whoever browses the repository list and is cut to make room;
    `unique` is kept whole, so two names cannot collide by having been cut at the same
    point — which also makes the name safe to derive from an identifier a deleted row
    releases, since the repository it left behind is named after a different one.
    """
    return f"{readable[: REPO_NAME_MAX_LENGTH - len(unique) - 1]}-{unique}"
