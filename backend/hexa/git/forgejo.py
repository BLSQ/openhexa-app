import base64
import logging
import os

import requests
from django.conf import settings

from hexa.git.client import GitClient

LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".md": "markdown",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".xml": "xml",
    ".svg": "xml",
    ".sh": "shell",
    ".r": "r",
    ".sql": "sql",
}

logger = logging.getLogger(__name__)

TOKEN_NAME = "openhexa-api"


class ForgejoAPIError(Exception):
    def __init__(self, method: str, url: str, status_code: int, detail: str = ""):
        self.method = method
        self.url = url
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"{method} {url}: {status_code} {detail}")


class ForgejoClient(GitClient):
    def __init__(self, *, url: str, username: str, password: str):
        self._url = url.rstrip("/")
        self._username = username
        self._password = password
        self._session = requests.Session()
        self._token = None

    def _ensure_token(self):
        if self._token is not None:
            return
        self._token = self._get_or_create_token()
        self._session.headers["Authorization"] = f"token {self._token}"

    def _get_or_create_token(self) -> str:
        url = f"{self._url}/api/v1/users/{self._username}/tokens"
        response = requests.get(
            url, auth=(self._username, self._password), allow_redirects=False
        )
        if response.status_code != 200:
            raise ForgejoAPIError("GET", url, response.status_code, response.text)

        for token in response.json():
            if token["name"] == TOKEN_NAME:
                requests.delete(
                    f"{url}/{token['id']}",
                    auth=(self._username, self._password),
                    allow_redirects=False,
                )
                break

        response = requests.post(
            url,
            auth=(self._username, self._password),
            json={"name": TOKEN_NAME, "scopes": ["all"]},
            allow_redirects=False,
        )
        if response.status_code != 201:
            raise ForgejoAPIError("POST", url, response.status_code, response.text)

        return response.json()["sha1"]

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        self._ensure_token()
        url = f"{self._url}/api/v1{path}"
        response = self._session.request(method, url, allow_redirects=False, **kwargs)
        if not response.ok:
            raise ForgejoAPIError(
                method.upper(), url, response.status_code, response.text
            )
        return response

    def create_organization(self, org_slug: str, display_name: str) -> dict:
        try:
            response = self._request(
                "POST",
                "/orgs",
                json={
                    "username": org_slug,
                    "full_name": display_name,
                    "visibility": "private",
                },
            )
            return response.json()
        except ForgejoAPIError as e:
            if e.status_code in (409, 422) and "already exists" in str(e):
                logger.info("Organization %s already exists", org_slug)
                return self._request("GET", f"/orgs/{org_slug}").json()
            raise

    def rename_organization(
        self, old_slug: str, new_slug: str, display_name: str
    ) -> dict | None:
        try:
            response = self._request(
                "PATCH",
                f"/orgs/{old_slug}",
                json={"username": new_slug, "full_name": display_name},
            )
            return response.json()
        except ForgejoAPIError as e:
            if e.status_code == 404:
                logger.info(
                    "Organization %s does not exist, nothing to rename", old_slug
                )
                return None
            raise

    def delete_organization(self, org_slug: str) -> None:
        try:
            self._request("DELETE", f"/orgs/{org_slug}")
        except ForgejoAPIError as e:
            if e.status_code == 404:
                logger.info(
                    "Organization %s does not exist, nothing to delete", org_slug
                )
                return
            raise

    def create_repository(self, repo_name: str) -> dict:
        try:
            response = self._request(
                "POST",
                "/user/repos",
                json={
                    "name": repo_name,
                    "auto_init": True,
                    "default_branch": "main",
                },
            )
            return response.json()
        except ForgejoAPIError as e:
            if e.status_code in (409, 422) and "already exists" in str(e):
                logger.info("Repository %s already exists", repo_name)
                return self._request(
                    "GET", f"/repos/{self._username}/{repo_name}"
                ).json()
            raise

    def create_org_repository(self, org_slug: str, repo_name: str) -> dict:
        try:
            response = self._request(
                "POST",
                f"/orgs/{org_slug}/repos",
                json={
                    "name": repo_name,
                    "auto_init": True,
                    "default_branch": "main",
                },
            )
            return response.json()
        except ForgejoAPIError as e:
            if e.status_code in (409, 422) and "already exists" in str(e):
                logger.info("Repository %s/%s already exists", org_slug, repo_name)
                return self._request("GET", f"/repos/{org_slug}/{repo_name}").json()
            raise

    def delete_repository(self, org_slug: str, repo_name: str) -> None:
        try:
            self._request("DELETE", f"/repos/{org_slug}/{repo_name}")
        except ForgejoAPIError as e:
            if e.status_code == 404:
                logger.info(
                    "Repository %s/%s does not exist, nothing to delete",
                    org_slug,
                    repo_name,
                )
                return
            raise

    def list_org_repositories(
        self, org_slug: str, page: int = 1, limit: int = 50
    ) -> list[dict]:
        try:
            response = self._request(
                "GET",
                f"/orgs/{org_slug}/repos",
                params={"page": page, "limit": limit},
            )
            return response.json()
        except ForgejoAPIError as e:
            if e.status_code == 404:
                logger.info("Organization %s does not exist", org_slug)
                return []
            raise

    def unarchive_repository(self, org_slug: str, repo_name: str) -> dict | None:
        try:
            response = self._request(
                "PATCH",
                f"/repos/{org_slug}/{repo_name}",
                json={"archived": False},
            )
            return response.json()
        except ForgejoAPIError as e:
            if e.status_code == 404:
                logger.info(
                    "Repository %s/%s does not exist, nothing to unarchive",
                    org_slug,
                    repo_name,
                )
                return None
            raise

    def archive_repository(self, org_slug: str, repo_name: str) -> dict | None:
        try:
            response = self._request(
                "PATCH",
                f"/repos/{org_slug}/{repo_name}",
                json={"archived": True},
            )
            return response.json()
        except ForgejoAPIError as e:
            if e.status_code == 404:
                logger.info(
                    "Repository %s/%s does not exist, nothing to archive",
                    org_slug,
                    repo_name,
                )
                return None
            raise

    def get_files_tree(
        self, repo_name: str, ref: str = "main", *, org_slug: str | None = None
    ) -> list[dict]:
        org_slug = org_slug or self._username
        response = self._request(
            "GET",
            f"/repos/{org_slug}/{repo_name}/git/trees/{ref}",
            params={"recursive": "true"},
        )
        return response.json().get("tree", [])

    def get_file(
        self,
        repo_name: str,
        path: str,
        ref: str = "main",
        *,
        org_slug: str | None = None,
    ) -> bytes:
        org_slug = org_slug or self._username
        response = self._request(
            "GET",
            f"/repos/{org_slug}/{repo_name}/contents/{path}",
            params={"ref": ref},
        )
        content = response.json().get("content", "")
        return base64.b64decode(content)

    def commit_files(
        self,
        repo_name: str,
        files: list[dict],
        message: str,
        author_name: str,
        author_email: str,
        *,
        org_slug: str | None = None,
    ) -> str:
        org_slug = org_slug or self._username
        existing_tree = {
            entry["path"] for entry in self.get_files_tree(repo_name, org_slug=org_slug)
        }

        operations = []
        for file in files:
            action = "update" if file["path"] in existing_tree else "create"
            content = file["content"]
            if isinstance(content, str):
                content = base64.b64encode(content.encode()).decode()
            elif isinstance(content, bytes):
                content = base64.b64encode(content).decode()
            operations.append(
                {
                    "operation": action,
                    "path": file["path"],
                    "content": content,
                }
            )

        response = self._request(
            "POST",
            f"/repos/{org_slug}/{repo_name}/contents",
            json={
                "branch": "main",
                "message": message,
                "author": {
                    "name": author_name,
                    "email": author_email,
                },
                "files": operations,
            },
        )
        return response.json().get("commit", {}).get("sha", "")

    def get_repository_files(
        self,
        repo_name: str,
        ref: str = "main",
        *,
        org_slug: str | None = None,
    ) -> list[dict]:
        """Fetch the full file tree and return a flat list of directory/file nodes
        with content and metadata.
        """
        tree = self.get_files_tree(repo_name, ref, org_slug=org_slug)
        nodes: list[dict] = []

        for entry in tree:
            path = entry.get("path", "")
            parent = "/".join(path.split("/")[:-1]) or None
            entry_type = entry.get("type", "")

            if entry_type == "tree":
                nodes.append(
                    {
                        "id": path,
                        "name": path.split("/")[-1],
                        "path": path,
                        "type": "directory",
                        "content": None,
                        "parent_id": parent,
                        "auto_select": False,
                        "language": None,
                        "line_count": None,
                    }
                )
            elif entry_type == "blob":
                content = None
                try:
                    raw = self.get_file(repo_name, path, ref, org_slug=org_slug)
                    content = raw.decode("utf-8", errors="replace")
                except (ForgejoAPIError, UnicodeDecodeError):
                    pass

                extension = os.path.splitext(path)[1].lower()
                nodes.append(
                    {
                        "id": path,
                        "name": path.split("/")[-1],
                        "path": path,
                        "type": "file",
                        "content": content,
                        "parent_id": parent,
                        "auto_select": path == "index.html",
                        "language": LANGUAGE_MAP.get(extension),
                        "line_count": content.count("\n") + 1 if content else None,
                    }
                )

        return nodes

    def commit_exists(self, org_slug: str, repo_name: str, sha: str) -> bool:
        try:
            self._request("GET", f"/repos/{org_slug}/{repo_name}/git/commits/{sha}")
            return True
        except ForgejoAPIError as e:
            if e.status_code == 404:
                return False
            raise

    def get_commits(
        self,
        org_slug: str,
        repo_name: str,
        ref: str = "main",
        page: int = 1,
        limit: int = 20,
    ) -> list[dict]:
        response = self._request(
            "GET",
            f"/repos/{org_slug}/{repo_name}/commits",
            params={"sha": ref, "page": page, "limit": limit},
        )
        return [
            {
                "id": c["sha"],
                "message": c["commit"]["message"],
                "author_name": c["commit"]["author"]["name"],
                "author_email": c["commit"]["author"]["email"],
                "date": c["commit"]["author"]["date"],
            }
            for c in response.json()
        ]


def get_forgejo_client() -> GitClient:
    return ForgejoClient(
        url=settings.GIT_SERVER_URL,
        username=settings.GIT_SERVER_ADMIN_USERNAME,
        password=settings.GIT_SERVER_ADMIN_PASSWORD,
    )
