import io
import logging
import zipfile
from base64 import b64decode, b64encode

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _base_url() -> str:
    return settings.GITEA_URL.rstrip("/")


def _api(path: str) -> str:
    return f"{_base_url()}/api/v1{path}"


def _basic_auth() -> tuple[str, str]:
    return (settings.GITEA_ADMIN_USERNAME, settings.GITEA_ADMIN_PASSWORD)


def create_repository(workspace_slug: str, pipeline_code: str) -> str:
    repo_name = f"{workspace_slug}_{pipeline_code}"
    resp = requests.post(
        _api("/user/repos"),
        auth=_basic_auth(),
        json={
            "name": repo_name,
            "auto_init": True,
            "default_branch": "main",
            "private": True,
        },
        timeout=10,
    )
    if resp.status_code == 409:
        return repo_name
    resp.raise_for_status()
    return repo_name


def delete_repository(repo_name: str):
    owner = settings.GITEA_ADMIN_USERNAME
    resp = requests.delete(
        _api(f"/repos/{owner}/{repo_name}"),
        auth=_basic_auth(),
        timeout=10,
    )
    if resp.status_code == 404:
        return
    resp.raise_for_status()


def commit_files(
    repo_name: str,
    files: list[dict],
    message: str,
    author_name: str = "OpenHEXA",
    author_email: str = "system@openhexa.local",
) -> str:
    owner = settings.GITEA_ADMIN_USERNAME

    existing_files = set()
    tree = get_files_tree(repo_name, "main")
    for entry in tree:
        existing_files.add(entry["path"])

    operations = []
    for f in files:
        content = f["content"]
        if isinstance(content, str):
            content = content.encode("utf-8")
        encoded = b64encode(content).decode("ascii")
        operation = "update" if f["path"] in existing_files else "create"
        operations.append(
            {
                "operation": operation,
                "path": f["path"],
                "content": encoded,
            }
        )

    resp = requests.post(
        _api(f"/repos/{owner}/{repo_name}/contents"),
        auth=_basic_auth(),
        json={
            "message": message,
            "files": operations,
            "author": {"name": author_name, "email": author_email},
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["commit"]["sha"]


def commit_zipfile(
    repo_name: str,
    zipfile_bytes: bytes,
    message: str,
    author_name: str = "OpenHEXA",
    author_email: str = "system@openhexa.local",
) -> str:
    files = []
    with zipfile.ZipFile(io.BytesIO(zipfile_bytes), "r") as zf:
        for entry in zf.infolist():
            if entry.is_dir():
                continue
            content = zf.read(entry.filename)
            files.append({"path": entry.filename, "content": content})

    if not files:
        files = [{"path": ".gitkeep", "content": b""}]

    return commit_files(repo_name, files, message, author_name, author_email)


def get_file(repo_name: str, path: str, ref: str) -> bytes:
    owner = settings.GITEA_ADMIN_USERNAME
    resp = requests.get(
        _api(f"/repos/{owner}/{repo_name}/contents/{path}"),
        auth=_basic_auth(),
        params={"ref": ref},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return b64decode(data["content"])


def get_files_tree(repo_name: str, ref: str) -> list[dict]:
    owner = settings.GITEA_ADMIN_USERNAME
    resp = requests.get(
        _api(f"/repos/{owner}/{repo_name}/git/trees/{ref}"),
        auth=_basic_auth(),
        params={"recursive": "true"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("tree", [])


def delete_file(
    repo_name: str,
    path: str,
    message: str,
    author_name: str = "OpenHEXA",
    author_email: str = "system@openhexa.local",
) -> str:
    owner = settings.GITEA_ADMIN_USERNAME
    resp = requests.delete(
        _api(f"/repos/{owner}/{repo_name}/contents/{path}"),
        auth=_basic_auth(),
        json={
            "message": message,
            "author": {"name": author_name, "email": author_email},
            "branch": "main",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["commit"]["sha"]


def get_archive_zip(repo_name: str, ref: str) -> bytes:
    owner = settings.GITEA_ADMIN_USERNAME
    resp = requests.get(
        _api(f"/repos/{owner}/{repo_name}/archive/{ref}.zip"),
        auth=_basic_auth(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content
