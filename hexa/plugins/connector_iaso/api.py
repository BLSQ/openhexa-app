from __future__ import annotations

import json

import requests

import hexa.plugins.connector_iaso.models as models


def get_api_token(iaso_account: models.IASOAccount):
    creds = {"username": iaso_account.username, "password": iaso_account.password}
    r = requests.post(iaso_account.api_url + "/token/", json=creds)
    token = r.json().get("access")
    return token


def get_forms_json(iaso_account: models.IASOAccount):
    api_token = get_api_token(iaso_account)
    headers = {"Authorization": "Bearer %s" % api_token}

    endpoint = iaso_account.api_url + "/forms/"
    r = requests.get(endpoint, headers=headers)
    j = json.loads(r.content)
    return j["forms"]
