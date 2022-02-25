from base64 import b64decode

from django.core.signing import Signer
from django.http import HttpRequest

from hexa.plugins.connector_accessmod.authentication import DAGRunUser
from hexa.plugins.connector_airflow.models import DAGRun


def dag_run_authentication_middleware(get_response):
    def middleware(request: HttpRequest):
        try:
            auth_type, encoded_token = request.headers["Authorization"].split(" ")
            if auth_type.lower() == "bearer":
                token = Signer().unsign(b64decode(encoded_token).decode("utf-8"))

                dag_run = DAGRun.objects.get(webhook_token=token)
                request.user = DAGRunUser(dag_run_id=dag_run.id)
        except (ValueError, KeyError):
            pass

        return get_response(request)

    return middleware
