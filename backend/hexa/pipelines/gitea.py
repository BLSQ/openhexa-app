import io
import logging
import zipfile
from base64 import b64decode, b64encode

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

_api_token: str | None = None


def _base_url() -> str:
    return settings.GITEA_URL.rstrip("/")


def _api(path: str) -> str:
    return f"{_base_url()}/api/v1{path}"


def _auth_headers() -> dict:
    token = get_api_token()
    return {"Authorization": f"token {token}"}


def get_api_token() -> str:
    global _api_token
    if _api_token is None:
        _api_token = ensure_admin_user()
    return _api_token


def ensure_admin_user() -> str:
    """Verify the Gitea admin user exists and create/refresh an API token.

    The admin user itself is created by Gitea on container startup via the
    GITEA_ADMIN_USER / GITEA_ADMIN_PASSWORD environment variables.
    """
    username = settings.GITEA_ADMIN_USERNAME
    password = settings.GITEA_ADMIN_PASSWORD

    token_name = "openhexa-backend"

    resp = requests.get(
        _api(f"/users/{username}/tokens"),
        auth=(username, password),
        timeout=10,
    )
    resp.raise_for_status()

    for token in resp.json():
        if token["name"] == token_name:
            requests.delete(
                _api(f"/users/{username}/tokens/{token['id']}"),
                auth=(username, password),
                timeout=10,
            )

    resp = requests.post(
        _api(f"/users/{username}/tokens"),
        auth=(username, password),
        json={"name": token_name, "scopes": ["all"]},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["sha1"]


def create_repository(workspace_slug: str, pipeline_code: str) -> str:
    repo_name = f"{workspace_slug}_{pipeline_code}"
    resp = requests.post(
        _api("/user/repos"),
        headers=_auth_headers(),
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
        headers=_auth_headers(),
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
        headers=_auth_headers(),
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
        headers=_auth_headers(),
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
        headers=_auth_headers(),
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
        headers=_auth_headers(),
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
        headers=_auth_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content
