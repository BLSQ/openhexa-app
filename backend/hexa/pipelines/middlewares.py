import binascii
from logging import getLogger

from django.core.signing import BadSignature, Signer
from django.http import HttpRequest

from hexa.pipelines.models import PipelineRun, PipelineRunState

from .authentication import PipelineRunUser

logger = getLogger(__name__)


def pipeline_run_authentication_middleware(get_response):
    """This middleware allows an Pipeline v2 run to authenticate through a simple token"""

    def middleware(request: HttpRequest):
        try:
            auth_type, token = request.headers["Authorization"].split(" ")
            if auth_type.lower() == "bearer":
                access_token = Signer().unsign_object(token)
                pipeline_run = PipelineRun.objects.get(
                    access_token=access_token, state=PipelineRunState.RUNNING
                )
                request.user = PipelineRunUser(pipeline_run=pipeline_run)
        except KeyError:
            pass  # No Authorization header
        except ValueError:
            logger.exception(
                "pipeline_run_authentication_middleware error",
            )
        except (UnicodeDecodeError, binascii.Error, BadSignature):
            pass
        except PipelineRun.DoesNotExist:
            pass
        return get_response(request)

    return middleware
