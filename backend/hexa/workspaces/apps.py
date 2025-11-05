import logging

from hexa.app import CoreAppConfig

logger = logging.getLogger(__name__)


class WorkspacesConfig(CoreAppConfig):
    name = "hexa.workspaces"
    label = "workspaces"

    ANONYMOUS_URLS = ["workspaces:credentials"]

    def ready(self):
        super().ready()
        self._check_jwt_configuration()

    def _check_jwt_configuration(self):
        from django.conf import settings

        from .jwt_utils import JWTConfigurationError, load_private_key

        private_key_pem = getattr(settings, "OPENHEXA_JWT_PRIVATE_KEY", None)

        if not private_key_pem:
            logger.warning(
                "OPENHEXA_JWT_PRIVATE_KEY is not configured. "
                "The issueWorkspaceToken mutation will not work until a valid RSA private key is provided."
            )
            return

        try:
            load_private_key()
            logger.info("JWT workspace token functionality is properly configured")
        except JWTConfigurationError as e:
            logger.warning(
                f"OPENHEXA_JWT_PRIVATE_KEY is configured but invalid: {e}. "
                "The issueWorkspaceToken mutation will not work until a valid RSA private key is provided."
            )
