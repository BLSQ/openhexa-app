import posixpath

from django.conf import settings
from django.urls import reverse

# Top-level folder of a workspace bucket whose files anyone can read once the
# workspace has public files enabled. Files have no model of their own, so the
# folder name is the whole marker.
PUBLIC_FOLDER = "public"


def is_safe_path(path: str) -> bool:
    if "\x00" in path or "~" in path:
        return False
    normalized = posixpath.normpath(path)
    if normalized.startswith("/"):
        return False
    parts = normalized.split("/")
    return ".." not in parts


def is_public_path(path: str) -> bool:
    """Whether `path` names a file inside the public folder (never the folder itself)."""
    parts = posixpath.normpath(path).split("/")
    return len(parts) > 1 and parts[0] == PUBLIC_FOLDER and parts[-1] != ""


def public_files_url(workspace) -> str:
    """Absolute base URL of the workspace's public files, ending with a slash."""
    return settings.BASE_URL + reverse(
        "files:public_file", kwargs={"workspace_slug": workspace.slug, "path": ""}
    )
