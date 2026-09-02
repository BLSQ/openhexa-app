import base64
from urllib.parse import quote

import requests
from django.conf import settings

from hexa.git.client import GitClient
from hexa.git.enums import FileEncoding
from hexa.git.exceptions import GitError, GitFileNotFound, GitFileTooLarge

MAX_INLINE_BLOB_SIZE = 10 * 1024 * 1024


def _commit_summary(payload: dict, *, fallback_id: str = "") -> dict:
    """Flatten a Forgejo commit payload into the shape every caller actually wants."""
    commit = payload.get("commit") or {}
    author = commit.get("author") or {}
    return {
        "id": payload.get("sha") or fallback_id,
        # A trailing newline is an artefact of how the message was written, not part
        # of it, and no consumer wants to strip it itself.
        "message": (commit.get("message") or "").strip(),
        "author_name": author.get("name", ""),
        "author_email": author.get("email", ""),
        "date": author.get("date", ""),
    }


class ForgejoAPIError(GitError):
    """A Forgejo call came back with an unexpected status.

    A `GitError` like the rest, so a caller that only needs "git is not answering"
    can say so without importing this backend; the status code is here for the few
    that act on a specific one.
    """

    def __init__(self, method: str, url: str, status_code: int, detail: str = ""):
        self.method = method
        self.url = url
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"{method} {url}: {status_code} {detail}")

    @property
    def already_exists(self) -> bool:
        return self.status_code == 409 or (
            self.status_code == 403 and "already exist" in self.detail.lower()
        )


def _is_failure_status(status_code: int) -> bool:
    return status_code >= 300


def _failure_detail(response: requests.Response) -> str:
    """Describe a failed response, naming the target of an unfollowed redirect."""
    location = response.headers.get("Location")
    if location:
        return f"redirected to {location}"
    return response.text


class ForgejoClient(GitClient):
    def __init__(self, *, url: str, username: str, password: str):
        self._url = url.rstrip("/")
        self._username = username
        self._session = requests.Session()
        self._session.auth = (username, password)

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self._url}/api/v1{path}"
        response = self._session.request(method, url, allow_redirects=False, **kwargs)
        if _is_failure_status(response.status_code):
            raise ForgejoAPIError(
                method.upper(), url, response.status_code, _failure_detail(response)
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

    def protect_branch(
        self, org_slug: str, repo_name: str, branch: str = "main"
    ) -> dict:
        response = self._request(
            "POST",
            f"/repos/{org_slug}/{repo_name}/branch_protections",
            json={
                "rule_name": branch,
                "enable_push": True,
                "block_admin_merge_override": True,
            },
        )
        return response.json()

    def add_collaborator(
        self, org_slug: str, repo_name: str, username: str, permission: str = "write"
    ) -> None:
        self._request(
            "PUT",
            f"/repos/{org_slug}/{repo_name}/collaborators/{username}",
            json={"permission": permission},
        )

    def ensure_user(self, username: str, password: str, email: str) -> None:
        """Create the user via the admin API, resyncing the password if it exists.

        Requires the client to be authenticated as a Forgejo admin. On a rotated
        password the PATCH keeps the account in sync so the proxy can keep
        authenticating as it.
        """
        if username == self._username:
            raise ValueError("Impossible to modify the current user.")

        try:
            self._request(
                "POST",
                "/admin/users",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "must_change_password": False,
                },
            )
            return
        except ForgejoAPIError as e:
            if not (e.status_code == 409 or "exist" in e.detail.lower()):
                raise

        self._request(
            "PATCH",
            f"/admin/users/{username}",
            json={
                "password": password,
                "must_change_password": False,
            },
        )

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
        try:
            response = self._request(
                "GET",
                f"/repos/{org_slug}/{repo_name}/contents/{quote(path, safe='/')}",
                params={"ref": ref},
            )
        except ForgejoAPIError as e:
            if e.status_code == 404:
                raise GitFileNotFound(path) from e
            raise
        payload = response.json()
        content = payload.get("content", "")
        size = payload.get("size", 0)
        if not content and size > 0:
            raise GitFileTooLarge(path, size)
        return base64.b64decode(content)

    def stream_file(
        self,
        repo_name: str,
        path: str,
        ref: str = "main",
        *,
        org_slug: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        org_slug = org_slug or self._username
        url = f"{self._url}/api/v1/repos/{org_slug}/{repo_name}/raw/{quote(path, safe='/')}"
        response = self._session.get(
            url,
            params={"ref": ref},
            headers={"Accept-Encoding": "identity", **(headers or {})},
            stream=True,
            allow_redirects=False,
        )
        if response.status_code == 404:
            response.close()
            raise GitFileNotFound(path)
        if response.status_code != 416 and _is_failure_status(response.status_code):
            detail = _failure_detail(response)
            response.close()
            raise ForgejoAPIError("GET", url, response.status_code, detail)
        return response

    def commit_files(
        self,
        repo_name: str,
        files: list[dict],
        message: str,
        author_name: str,
        author_email: str,
        *,
        org_slug: str | None = None,
        delete_paths: list[str] | None = None,
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
            if file.get("encoding") == FileEncoding.BASE64:
                encoded = content
            else:  # text encoding
                encoded = base64.b64encode(content.encode()).decode()
            op = {
                "operation": "update" if is_update else "create",
                "path": path,
                "content": encoded,
            }
            if is_update:
                op["sha"] = existing_tree[path]
            operations.append(op)

        for path in delete_paths or []:
            if path in existing_tree:
                operations.append(
                    {
                        "operation": "delete",
                        "path": path,
                        "sha": existing_tree[path],
                    }
                )

        if not operations:
            return commits[0]["id"] if commits else ""

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
        """Fetch the full file tree and return a flat list with path, type, content, and encoding.

        Content is either UTF-8 (for text files) or base64 (for binary files).
        To detect if a blob is binary, check for a NULL byte or a failed UTF-8 decode.
        Blobs too large to read carry too_large=True and no content.
        """
        tree = self.get_files_tree(repo_name, ref, org_slug=org_slug)
        nodes: list[dict] = []

        for entry in tree:
            path = entry.get("path", "")
            entry_type = entry.get("type", "")

            if entry_type == "tree":
                nodes.append(
                    {
                        "path": path,
                        "type": "directory",
                        "content": None,
                        "encoding": None,
                        "size": None,
                        "too_large": False,
                    }
                )
                continue
            if entry_type != "blob":
                continue

            size = entry.get("size") or 0
            too_large_node = {
                "path": path,
                "type": "file",
                "content": None,
                "encoding": None,
                "size": size,
                "too_large": True,
            }
            if size >= MAX_INLINE_BLOB_SIZE:
                nodes.append(too_large_node)
                continue

            try:
                raw = self.get_file(repo_name, path, ref, org_slug=org_slug)
            except GitFileTooLarge as e:
                nodes.append({**too_large_node, "size": e.size})
                continue
            content: str
            encoding: FileEncoding
            if b"\x00" not in raw:
                try:
                    content = raw.decode("utf-8")
                    encoding = FileEncoding.TEXT
                except UnicodeDecodeError:
                    content = base64.b64encode(raw).decode("ascii")
                    encoding = FileEncoding.BASE64
            else:
                content = base64.b64encode(raw).decode("ascii")
                encoding = FileEncoding.BASE64

            nodes.append(
                {
                    "path": path,
                    "type": "file",
                    "content": content,
                    "encoding": encoding,
                    "size": size,
                    "too_large": False,
                }
            )

        return nodes

    def get_commit(self, org_slug: str, repo_name: str, sha: str) -> dict:
        response = self._request(
            "GET", f"/repos/{org_slug}/{repo_name}/git/commits/{sha}"
        )
        return _commit_summary(response.json(), fallback_id=sha)

    def get_commit_diff(self, org_slug: str, repo_name: str, sha: str) -> str:
        response = self._request(
            "GET", f"/repos/{org_slug}/{repo_name}/git/commits/{sha}.diff"
        )
        return response.text

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
        return [_commit_summary(commit) for commit in response.json()]


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
