import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from config import logging


class DHIS2ClientException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        self.log_error()

    def __str__(self):
        return self.message

    def log_error(self):
        logging.error(f"DHIS2 Cient Error : {self.message}")


class DHIS2Client(requests.Session):
    def __init__(self, url: str, username: str, password: str):
        super().__init__()
        self.url = self.parse_api_url(url)
        self.username = username
        self.password = password

        self.authenticate()

    @staticmethod
    def parse_api_url(url: str) -> str:
        """Ensure that API URL is correctly formatted."""
        url = url.rstrip("/")
        if "/api" not in url:
            url += "/api"
        return url

    def authenticate(self):
        self.auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=3,
                backoff_factor=5,
                allowed_methods=["HEAD", "GET"],
                status_forcelist=[429, 500, 502, 503, 504],
            )
        )
        self.mount("https://", adapter)
        self.mount("http://", adapter)

    def request(self, method: str, url: str, *args, **kwargs) -> requests.Response:
        try:
            resp = super().request(method, url, *args, **kwargs)
            self.raise_if_error(resp)
            return resp
        except requests.RequestException as exc:
            logging.exception(exc)
            raise

    def raise_if_error(self, r: requests.Response) -> None:
        if r.status_code != 200 and "json" in r.headers["content-type"]:
            msg = r.json()
            if msg.get("status") == "ERROR":
                raise DHIS2ClientException(
                    f"{msg.get('status')} {msg.get('httpStatusCode')}: {msg.get('message')}"
                )

        r.raise_for_status()
