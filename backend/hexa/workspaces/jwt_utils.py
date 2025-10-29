import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_JWT_ISSUER = "https://app.openhexa.org"
DEFAULT_JWT_AUDIENCE = "openhexa-clients"
DEFAULT_JWT_TTL = 3600


class JWTConfigurationError(Exception):
    pass


class JWTGenerationError(Exception):
    pass


def load_private_key() -> Optional[bytes]:
    """
    Load and validate the RSA private key from environment configuration.

    Returns
    -------
        The private key in PEM format as bytes, or None if not configured.

    Raises
    ------
        JWTConfigurationError: If the key is malformed or cannot be loaded.
    """
    private_key_pem = getattr(settings, "OPENHEXA_JWT_PRIVATE_KEY", None)

    if not private_key_pem:
        return None

    try:
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode()
            if isinstance(private_key_pem, str)
            else private_key_pem,
            password=None,
            backend=default_backend(),
        )
        return private_key
    except Exception as e:
        logger.error(f"Failed to load JWT private key: {e}")
        raise JWTConfigurationError(f"Invalid private key format: {e}")


def generate_workspace_jwt(
    user_id: str,
    user_email: str,
    workspace_id: str,
    workspace_slug: str,
    role: str,
    ttl_seconds: Optional[int] = None,
) -> dict:
    """
    Generate a JWT token for workspace access.

    Args:
        user_id: The unique identifier of the user
        user_email: The email address of the user
        workspace_id: The unique identifier of the workspace
        workspace_slug: The slug of the workspace
        role: The user's role in the workspace (OWNER, ADMIN, EDITOR, VIEWER)
        ttl_seconds: Token time-to-live in seconds (defaults to settings)

    Returns
    -------
        A dictionary containing:
            - token: The encoded JWT string
            - expires_at: The expiration datetime

    Raises
    ------
        JWTConfigurationError: If private key is not configured
        JWTGenerationError: If token generation fails
    """
    private_key = load_private_key()

    if private_key is None:
        raise JWTConfigurationError("Private key is not configured")

    if ttl_seconds is None:
        ttl_seconds = getattr(settings, "OPENHEXA_JWT_TTL", DEFAULT_JWT_TTL)

    try:
        now = datetime.now(timezone.utc)

        if now.timestamp() < 0:
            raise JWTGenerationError("System clock error: negative timestamp")

        expires_at = now + timedelta(seconds=ttl_seconds)

        issuer = getattr(settings, "OPENHEXA_JWT_ISSUER", DEFAULT_JWT_ISSUER)
        audience = getattr(settings, "OPENHEXA_JWT_AUDIENCE", DEFAULT_JWT_AUDIENCE)

        payload = {
            "sub": user_id,
            "iss": issuer,
            "aud": audience,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "jti": str(uuid.uuid4()),
            "https://app.openhexa.org/claims/workspace": {
                "id": workspace_id,
                "slug": workspace_slug,
            },
            "https://app.openhexa.org/claims/workspace_role": role,
            "https://app.openhexa.org/claims/user": {
                "id": user_id,
                "email": user_email,
            },
        }

        headers = {"alg": "RS256", "typ": "JWT"}

        kid = getattr(settings, "OPENHEXA_JWT_KID", None)
        if kid:
            headers["kid"] = kid

        token = jwt.encode(payload, private_key, algorithm="RS256", headers=headers)

        return {"token": token, "expires_at": expires_at}

    except JWTGenerationError:
        raise
    except Exception as e:
        logger.error(f"Failed to generate JWT: {e}")
        raise JWTGenerationError(f"Token generation failed: {e}")
