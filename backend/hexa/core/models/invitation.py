import base64

from django.core.signing import TimestampSigner
from django.db import models
from django.db.models import EmailField

from hexa.core.models.base import Base


class InvitationManager(models.Manager):
    """Base manager for invitation models that use token-based lookups."""

    def get_by_token(self, token: str):
        signer = TimestampSigner()
        decoded_value = base64.b64decode(token).decode("utf-8")
        # Token valid for 48h
        invitation_id = signer.unsign(decoded_value, max_age=48 * 3600)
        return self.get(id=invitation_id)


class Invitation(Base):
    """Abstract base model for invitation-like models that can be accepted."""

    email = EmailField(db_collation="case_insensitive")

    class Meta:
        abstract = True

    def generate_token(self) -> str:
        signer = TimestampSigner()
        return base64.b64encode(signer.sign(str(self.id)).encode("utf-8")).decode()

    def get_tracking_properties(self) -> dict:
        raise NotImplementedError(
            "Classes having the Invitation behavior should implement get_tracking_properties()"
        )

    def accept(self, user) -> None:
        raise NotImplementedError(
            "Classes having the Invitation behavior should implement accept()"
        )
