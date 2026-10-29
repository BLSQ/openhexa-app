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
