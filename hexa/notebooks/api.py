import typing

import requests
from django.conf import settings


def get_user(username: str) -> typing.Optional[typing.Mapping[str, typing.Any]]:
    user_response = requests.get(
        f"{settings.NOTEBOOKS_HUB_URL}/api/users/{username}",
        headers={"Authorization": f"token {settings.HUB_API_TOKEN}"},
    )
    if user_response.status_code == 404:
        return None
    user_response.raise_for_status()

    return user_response.json()


def create_user(username: str):
    user_response = requests.post(
        f"{settings.NOTEBOOKS_HUB_URL}/api/users/{username}",
        headers={"Authorization": f"token {settings.HUB_API_TOKEN}"},
    )
    user_response.raise_for_status()


def create_server(username: str, server_name: str, cookies: typing.Mapping[str, str]):
    server_response = requests.post(
        f"{settings.NOTEBOOKS_HUB_URL}/api/users/{username}/servers/{server_name}",
        headers={"Authorization": f"token {settings.HUB_API_TOKEN}"},
        cookies=cookies,
    )
    server_response.raise_for_status()


def server_ready(username: str, server_name: str = "") -> bool:
    r = requests.get(
        f"{settings.NOTEBOOKS_HUB_URL}/api/users/{username}",
        headers={"Authorization": f"token {settings.HUB_API_TOKEN}"},
    )
    r.raise_for_status()
    user_model = r.json()
    servers = user_model.get("servers", {})
    if server_name not in servers:
        return False

    server = servers[server_name]
    return server["ready"]
