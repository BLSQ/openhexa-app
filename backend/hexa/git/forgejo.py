import base64
import logging

import requests
from django.conf import settings

from hexa.git.client import GitClient

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
            json={
                "name": TOKEN_NAME,
                "scopes": ["write:organization", "write:repository"],
            },
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

    def create_repository(self, repo_name: str) -> dict:
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

    def create_org_repository(
        self, org_slug: str, repo_name: str, *, auto_init: bool = True
    ) -> dict:
        response = self._request(
            "POST",
            f"/orgs/{org_slug}/repos",
            json={
                "name": repo_name,
                "auto_init": auto_init,
                "default_branch": "main",
            },
        )
        return response.json()

    def list_org_repositories(
        self, org_slug: str, page: int = 1, limit: int = 50
    ) -> list[dict]:
        response = self._request(
            "GET",
            f"/orgs/{org_slug}/repos",
            params={"page": page, "limit": limit},
        )
        return response.json()

    def unarchive_repository(self, org_slug: str, repo_name: str) -> dict:
        response = self._request(
            "PATCH",
            f"/repos/{org_slug}/{repo_name}",
            json={"archived": False},
        )
        return response.json()

    def archive_repository(self, org_slug: str, repo_name: str) -> dict:
        response = self._request(
            "PATCH",
            f"/repos/{org_slug}/{repo_name}",
            json={"archived": True},
        )
        return response.json()

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
        commits = self.get_commits(org_slug, repo_name, limit=1)
        if commits:
            existing_tree = {
                entry["path"]: entry.get("sha", "")
                for entry in self.get_files_tree(repo_name, org_slug=org_slug)
            }
        else:
            existing_tree = {}

        operations = []
        for file in files:
            path = file["path"]
            is_update = path in existing_tree
            content = file["content"]
            if isinstance(content, str):
                content = base64.b64encode(content.encode()).decode()
            elif isinstance(content, bytes):
                content = base64.b64encode(content).decode()
            op = {
                "operation": "update" if is_update else "create",
                "path": path,
                "content": content,
            }
            if is_update:
                op["sha"] = existing_tree[path]
            operations.append(op)

        branch_key = "branch" if existing_tree else "new_branch"
        response = self._request(
            "POST",
            f"/repos/{org_slug}/{repo_name}/contents",
            json={
                branch_key: "main",
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
        """Fetch the full file tree and return a flat list with path, type, and content."""
        tree = self.get_files_tree(repo_name, ref, org_slug=org_slug)
        nodes: list[dict] = []

        for entry in tree:
            path = entry.get("path", "")
            entry_type = entry.get("type", "")

            if entry_type == "tree":
                nodes.append({"path": path, "type": "directory", "content": None})
            elif entry_type == "blob":
                raw = self.get_file(repo_name, path, ref, org_slug=org_slug)
                content = raw.decode("utf-8", errors="replace")
                nodes.append({"path": path, "type": "file", "content": content})

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
        try:
            response = self._request(
                "GET",
                f"/repos/{org_slug}/{repo_name}/commits",
                params={"sha": ref, "page": page, "limit": limit},
            )
        except ForgejoAPIError as e:
            if e.status_code == 409:
                return []
            raise
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


_forgejo_client: ForgejoClient | None = None


def get_forgejo_client() -> GitClient:
    global _forgejo_client
    if _forgejo_client is None:
        _forgejo_client = ForgejoClient(
            url=settings.GIT_SERVER_URL,
            username=settings.GIT_SERVER_ADMIN_USERNAME,
            password=settings.GIT_SERVER_ADMIN_PASSWORD,
        )
    return _forgejo_client
