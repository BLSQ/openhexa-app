import binascii
from logging import getLogger

from django.core.signing import BadSignature, Signer
from django.http import HttpRequest

from hexa.plugins.connector_airflow.models import DAGRun

from .authentication import DAGRunUser

logger = getLogger(__name__)


def dag_run_authentication_middleware(get_response):
    """This middleware allows an Airflow DAG run to authenticate through a simple token"""

    def middleware(request: HttpRequest):
        try:
            auth_type, token = request.headers["Authorization"].split(" ")
            if auth_type.lower() == "bearer":
                token = Signer().unsign_object(token)
                dag_run = DAGRun.objects.get(webhook_token=token)
                request.user = DAGRunUser(dag_run=dag_run)
        except KeyError:
            pass  # No Authorization header
        except ValueError:
            logger.exception(
                "dag_run_authentication_middleware error",
            )
        except (UnicodeDecodeError, binascii.Error, BadSignature):
            pass
        except DAGRun.DoesNotExist:
            pass
        return get_response(request)

    return middleware
