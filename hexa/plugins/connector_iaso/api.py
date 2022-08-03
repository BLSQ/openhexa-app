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


def get_orgunittypes_json(iaso_account: models.IASOAccount, api_token: str):
    headers = {"Authorization": "Bearer %s" % api_token}
    endpoint = iaso_account.api_url + "/orgunittypes/"
    r = requests.get(endpoint, headers=headers)
    j = json.loads(r.content)
    return j["orgUnitTypes"]


def get_orgunits_level12(iaso_account: models.IASOAccount):
    api_token = get_api_token(iaso_account)
    orgunittypes = get_orgunittypes_json(iaso_account, api_token)

    level1 = []
    level2 = []
    for orgtype in orgunittypes:
        if orgtype["depth"] == 1:
            level1.append(orgtype["id"])
        elif orgtype["depth"] == 2:
            level2.append(orgtype["id"])

    endpoint = iaso_account.api_url + "/orgunits/"
    headers = {"Authorization": "Bearer %s" % api_token}
    orgunits = []
    for id in level1:
        r = requests.get(endpoint, headers=headers, params={"orgUnitTypeId": id})
        j = json.loads(r.content)
        orgunits += j["orgUnits"]
    for id in level2:
        continueloop = True
        page = 1
        while continueloop:
            r = requests.get(
                endpoint,
                headers=headers,
                params={"orgUnitTypeId": id, "limit": 200, "page": page},
            )
            j = json.loads(r.content)
            orgunits += j["orgunits"]
            page += 1
            if (j["has_next"] is False) or (page > 300):
                continueloop = False

    return orgunits
