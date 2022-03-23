import binascii
from base64 import b64decode
from logging import getLogger

from django.core.signing import Signer
from django.http import HttpRequest

from hexa.plugins.connector_accessmod.authentication import DAGRunUser
from hexa.plugins.connector_airflow.models import DAGRun

logger = getLogger(__name__)


def dag_run_authentication_middleware(get_response):
    """This middleware allows an Airflow DAG run to authenticate through a simple token"""

    def middleware(request: HttpRequest):
        try:
            auth_type, encoded_token = request.headers["Authorization"].split(" ")
            if auth_type.lower() == "bearer":
                token = Signer().unsign(b64decode(encoded_token).decode("utf-8"))
                dag_run = DAGRun.objects.get(webhook_token=token)
                request.user = DAGRunUser(dag_run=dag_run)
        except KeyError:
            pass  # No Authorization header
        except ValueError as e:
            logger.exception(
                "dag_run_authentication_middleware error",
            )
        except (UnicodeDecodeError, binascii.Error):
            pass
        except DAGRun.DoesNotExist:
            pass
        return get_response(request)

    return middleware
