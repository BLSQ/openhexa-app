import base64
import logging

import requests

logger = logging.getLogger(__name__)

TOKEN_NAME = "openhexa-api"


class ForgejoAPIError(Exception):
    def __init__(self, method: str, url: str, status_code: int, detail: str = ""):
        self.method = method
        self.url = url
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"{method} {url}: {status_code} {detail}")


class ForgejoClient:
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
            if e.status_code == 409:
                logger.info("Repository %s already exists", repo_name)
                return self._request(
                    "GET", f"/repos/{self._username}/{repo_name}"
                ).json()
            raise

    def delete_repository(self, repo_name: str) -> None:
        try:
            self._request("DELETE", f"/repos/{self._username}/{repo_name}")
        except ForgejoAPIError as e:
            if e.status_code == 404:
                logger.info(
                    "Repository %s does not exist, nothing to delete", repo_name
                )
                return
            raise

    def get_files_tree(self, repo_name: str, ref: str = "main") -> list[dict]:
        response = self._request(
            "GET",
            f"/repos/{self._username}/{repo_name}/git/trees/{ref}",
            params={"recursive": "true"},
        )
        return response.json().get("tree", [])

    def get_file(self, repo_name: str, path: str, ref: str = "main") -> bytes:
        response = self._request(
            "GET",
            f"/repos/{self._username}/{repo_name}/contents/{path}",
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
    ) -> str:
        existing_tree = {entry["path"] for entry in self.get_files_tree(repo_name)}

        operations = []
        for file in files:
            action = "update" if file["path"] in existing_tree else "create"
            operations.append(
                {
                    "operation": action,
                    "path": file["path"],
                    "content": file["content"],
                }
            )

        response = self._request(
            "POST",
            f"/repos/{self._username}/{repo_name}/contents",
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
