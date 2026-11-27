from dataclasses import dataclass


@dataclass(frozen=True)
class CopyOptions:
    all_dataset_versions: bool = False
    """Copy every version of each dataset instead of only the latest one."""

    include_connection_secrets: bool = True
    """Copy secret connection field values; when False they are created empty."""

    same_server: bool = False
    """Both workspaces are on this server: also copy the database and static web
    apps, which need its database and git server directly."""

    target_countries: tuple[str, ...] | None = None
    """Country codes of a new target workspace; None copies the source's."""

    created_by_id: str | None = None
    """Owner of the resources written directly with the ORM (static web apps).

    Set when the copy acts as its requester, who then owns everything copied.
    None keeps each source resource's own author, as admin copies do.
    """
