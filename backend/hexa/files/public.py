"""The "public" folder at the root of a workspace bucket, whose files are served without
authentication once the workspace enables public files (see `views.public_file`).
"""

from django.conf import settings
from django.urls import reverse

from hexa.files import storage
from hexa.files.utils import is_safe_path

PUBLIC_FOLDER = "public/"


def public_files_base_url(workspace) -> str | None:
    """URL under which the public files of a workspace are served, ending with a slash.

    None while they are not served: the instance or the workspace has the feature off,
    or the workspace is archived.
    """
    if (
        not settings.PUBLIC_FILES_ENABLED
        or not workspace.public_files_enabled
        or workspace.archived
    ):
        return None
    return (
        f"{settings.BASE_URL}{reverse('files:public_file', args=[workspace.slug, ''])}"
    )


def find_public_file(bucket_name: str, path: str) -> str:
    """Storage key of a file of the public folder, given its path inside that folder.

    Raises `storage.exceptions.NotFound` for anything that must not be served: unsafe
    paths, hidden files and folders.
    """
    if not path or not is_safe_path(path):
        raise storage.exceptions.NotFound
    if any(part.startswith(".") for part in path.split("/")):
        raise storage.exceptions.NotFound
    key = f"{PUBLIC_FOLDER}{path}"
    # Some backends resolve directory keys and sign URLs for any key, so the object
    # has to be an existing file.
    if storage.get_bucket_object(bucket_name, key).type != "file":
        raise storage.exceptions.NotFound
    return key


def public_folder_exists(bucket_name: str) -> bool:
    """Whether the public folder exists in a bucket.

    Object storages have no real folders: the folder is either a placeholder object created
    from the UI, or only implied by the keys of the files uploaded in it.
    """
    try:
        storage.get_bucket_object(bucket_name, PUBLIC_FOLDER)
        return True
    except storage.exceptions.NotFound:
        pass
    try:
        page = storage.list_bucket_objects(
            bucket_name, prefix=PUBLIC_FOLDER, per_page=1, ignore_hidden_files=False
        )
    except storage.exceptions.NotFound:
        return False
    return bool(page.items)
