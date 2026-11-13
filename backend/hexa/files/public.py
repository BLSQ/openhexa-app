"""The "public" folder at the root of a workspace bucket, whose files are served without
authentication once the workspace enables public files (see `views.public_file`).
"""

from hexa.files import storage

PUBLIC_FOLDER = "public/"


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
