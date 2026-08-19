from dataclasses import dataclass


@dataclass(frozen=True)
class CopyOptions:
    all_dataset_versions: bool = False
    """Copy every version of each dataset instead of only the latest one."""
