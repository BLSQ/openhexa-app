from requests.adapters import HTTPAdapter
from starlette import requests
from urllib3 import Retry

from hexa.catalog.queue import logger


class DHIS2Connection:
    url: str = None
    username: str = None
    password: str = None


class DHIS2Exception(Exception):
    pass


class DHIS2Client:
    def __init__(self, connection: DHIS2Connection):
        self.url = connection.url

        self.session = requests.Session()
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=3,
                backoff_factor=5,
                allowed_methods=["HEAD", "GET"],
                status_forcelist=[429, 500, 502, 503, 504],
            )
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.session = self.authenticate(connection.username, connection.password)
        self.PAGE_SIZE = 1000

        self.DEFAULT_EXPIRE_TIME = 86400
        self.EXPIRE_TIMES = {
            "dataValueSets": 604800,
            "analytics": 604800,
            "system": 60,
        }

    def authenticate(self, username: str, password: str) -> requests.Session():
        s = requests.Session()
        s.auth = requests.auth.HTTPBasicAuth(username, password)
        r = s.get(f"{self.url}/system/ping")

        if r.status_code in [200, 406]:
            logger.info(f"Logged in to '{self.url}' as '{username}'")
        else:
            self.raise_if_error(r)
        return s

    def request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ) -> requests.Response:
        url = f"{self.url}/{endpoint}"
        response = self.session.request(method, url, params=params, json=data)
        response.raise_for_status()
        return response

    def raise_if_error(self, r: requests.Response) -> None:
        if r.status_code != 200 and "json" in r.headers["content-type"]:
            msg = r.json()
            if msg.get("status") == "ERROR":
                raise DHIS2Exception(
                    f"{msg.get('status')} {msg.get('httpStatusCode')}: {msg.get('message')}"
                )

        r.raise_for_status()
