from dataclasses import dataclass


@dataclass(frozen=True)
class CopyOptions:
    all_dataset_versions: bool = False
    """Copy every version of each dataset instead of only the latest one."""

    skip_existing_files: bool = False
    """Skip files already present on the target with the same key and size.

    Only files need this switch: the other copiers always skip resources that
    already exist on the target.
    """
