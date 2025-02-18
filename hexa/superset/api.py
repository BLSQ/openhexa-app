from typing import Optional, TypedDict

import requests
from requests.exceptions import HTTPError


class SupersetUser(TypedDict):
    username: str
    first_name: str
    last_name: str


class SupersetResource(TypedDict):
    type: str
    id: str


class SupersetError(Exception):
    """Base exception for Superset API errors"""

    def __init__(self, message: str, response: Optional[requests.Response] = None):
        self.message = message
        self.response = response
        super().__init__(self.message)


class SupersetAuthError(SupersetError):
    """Exception raised for authentication related errors"""

    pass


class SupersetClient:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.session = requests.Session()

    @property
    def base_url(self):
        return self.url.rstrip("/")

    def authenticate(self):
        headers = {"Content-Type": "application/json"}

        # Log in to Superset to get access_token
        payload = {
            "username": self.username,
            "password": self.password,
            "provider": "db",
            "refresh": True,  # TODO: Not Implemented
        }
        try:
            response = requests.post(
                self.base_url + "/api/v1/security/login", json=payload, headers=headers
            )
            response.raise_for_status()
            access_token = response.json()["access_token"]
            headers["Authorization"] = f"Bearer {access_token}"

            # Fetch CSRF token
            response = requests.get(
                self.base_url + "/api/v1/security/csrf_token/", headers=headers
            )
            response.raise_for_status()
            headers["X-CSRF-TOKEN"] = response.json()["result"]
            headers["Cookie"] = response.headers.get("Set-Cookie")
            headers["Referer"] = self.base_url

            self.session.headers.update(headers)
        except HTTPError as e:
            if e.response.status_code == 401:
                raise SupersetAuthError(
                    "Authentication failed: Invalid username or password",
                    response=e.response,
                )
            raise SupersetError(
                f"Failed to authenticate with Superset: {e}", response=e.response
            )

    def get_guest_token(
        self,
        user: SupersetUser,
        resources: list[SupersetResource],
        rls: Optional[list[str]] = None,
    ):
        """Get a guest token for a user to access a resource

        Args:
            user (SupersetUser): Dictionary containing user information (username, first_name, last_name)
            resources (List[SupersetResource]): List of resources to access, each containing type and id
            rls (List[str], optional): The roles to access the resources with. Defaults to None.
        """
        payload = {
            "user": user,
            "resources": resources,
            "rls": rls or [],
        }
        try:
            response = self.session.post(
                self.base_url + "/api/v1/security/guest_token/", json=payload
            )
            response.raise_for_status()
            return response.json()["token"]
        except HTTPError as e:
            raise SupersetError(f"Failed to get guest token: {e}", response=e.response)
