import typing
from urllib.parse import urljoin

import requests
from django.utils import timezone


class AirflowAPIError(Exception):
    pass


class AirflowAPIClient:
    def __init__(self, *, url: str, username: str, password: str):
        self._url = url
        self._session = requests.Session()
        self._session.auth = (username, password)

    def list_dags(self) -> typing.Dict:
        url = urljoin(self._url, "dags")
        response = self._session.get(url, allow_redirects=False)
        if response.status_code != 200:
            raise AirflowAPIError(f"GET {url}: got {response.status_code}")

        return response.json()

    def list_task_instances(self, dag_id, run_id) -> typing.Dict:
        url = urljoin(self._url, "dags")
        url = f"{url}/{dag_id}/dagRuns/{run_id}/taskInstances"
        response = self._session.get(url, allow_redirects=False)
        if response.status_code != 200:
            raise AirflowAPIError(f"GET {url}: got {response.status_code}")

        return response.json()

    def get_logs(self, dag_id, run_id, task):
        url = urljoin(self._url, "dags")
        url = f"{url}/{dag_id}/dagRuns/{run_id}/taskInstances/{task}/logs/1"
        response = self._session.get(url, allow_redirects=False)
        if response.status_code != 200:
            raise AirflowAPIError(f"GET {url}: got {response.status_code}")

        return response.text

    def trigger_dag_run(
        self, dag_id: str, run_type: str, conf: typing.Mapping[str, typing.Any]
    ) -> typing.Dict:
        url = urljoin(self._url, f"dags/{dag_id}/dagRuns")
        formated_time = timezone.now().isoformat()
        dag_run_id = f"{run_type.lower()}__{formated_time}"
        response = self._session.post(
            url,
            json={
                "execution_date": formated_time,
                "conf": conf,
                "dag_run_id": dag_run_id,
            },
            allow_redirects=False,
        )
        if response.status_code != 200:
            raise AirflowAPIError(f"POST {url}: got {response.status_code}")

        return response.json()

    def list_dag_runs(
        self, dag_id: str, limit: int = 100, get_all: bool = False
    ) -> typing.Dict:
        results = []
        continueloop = True
        offset = 0
        while continueloop:
            url = urljoin(
                self._url,
                f"dags/{dag_id}/dagRuns?order_by=-end_date&limit={limit}&offset={offset}",
            )
            response = self._session.get(url, allow_redirects=False)
            if response.status_code != 200:
                raise AirflowAPIError(f"GET {url}: got {response.status_code}")
            j = response.json()
            results += j["dag_runs"]

            offset += limit
            if j["total_entries"] <= offset or not get_all:
                continueloop = False

        return results

    def get_dag_run(self, dag_id: str, run_id: str) -> typing.Dict:
        url = urljoin(
            self._url,
            f"dags/{dag_id}/dagRuns/{run_id}",
        )

        response = self._session.get(url, allow_redirects=False)
        if response.status_code != 200:
            raise AirflowAPIError(f"GET {url}: got {response.status_code}")

        return response.json()

    def list_variables(self) -> typing.Dict:
        url = urljoin(self._url, "variables")
        response = self._session.get(url, allow_redirects=False)
        if response.status_code != 200:
            raise AirflowAPIError(f"GET {url}: got {response.status_code}")

        return {e["key"]: e["value"] for e in response.json()["variables"]}

    def update_variable(self, key, value):
        url = urljoin(self._url, f"variables/{key}")
        response = self._session.patch(
            url,
            json={
                "key": key,
                "value": value,
            },
            allow_redirects=False,
        )
        if response.status_code != 200:
            raise AirflowAPIError(f"PATCH {url}: got {response.status_code}")

        return response.json()

    def create_variable(self, key, value):
        url = urljoin(self._url, "variables")
        response = self._session.post(
            url,
            json={
                "key": key,
                "value": value,
            },
            allow_redirects=False,
        )
        if response.status_code != 200:
            raise AirflowAPIError(f"POST {url}: got {response.status_code}")

        return response.json()

    def unpause_dag(self, dag_id):
        url = urljoin(self._url, "/".join(["dags", dag_id]))
        response = self._session.patch(
            url,
            json={"is_paused": False},
            allow_redirects=False,
        )
        if response.status_code != 200:
            raise AirflowAPIError(f"PATCH {url}: got {response.status_code}")

        return response.json()
