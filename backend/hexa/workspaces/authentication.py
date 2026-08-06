import abc
import binascii
import time
from logging import getLogger

from django.conf import settings
from django.core.signing import BadSignature, Signer

from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembership

logger = getLogger(__name__)


class WorkspaceToken(abc.ABC):
    """A signed bearer token granting a user access to a single workspace."""

    def __init__(self, user: User, workspace: Workspace):
        self.user = user
        self.workspace = workspace

    @abc.abstractmethod
    def payload(self) -> str | dict:
        """The object to sign for this token."""

    @classmethod
    @abc.abstractmethod
    def from_payload(cls, payload) -> "WorkspaceToken | None":
        """Rebuild a token from its payload, or ``None`` if it no longer grants access."""

    def sign(self) -> str:
        return Signer().sign_object(self.payload())

    @classmethod
    def issue(
        cls,
        *,
        user: User,
        workspace: Workspace,
        membership: WorkspaceMembership | None,
    ) -> "WorkspaceToken":
        """Mint the right token for ``user`` in ``workspace``.

        Members reuse their revocable membership token; users with implicit
        access get an identity token.
        """
        if membership is not None:
            return MembershipToken(membership)
        return IdentityToken(user, workspace)

    @classmethod
    def authenticate(cls, raw_token: str) -> "WorkspaceToken | None":
        """Resolve a signed token string, or ``None`` if it is invalid or revoked."""
        try:
            payload = Signer().unsign_object(raw_token)
        except (UnicodeDecodeError, binascii.Error, BadSignature):
            return None

        if isinstance(payload, str):
            token = MembershipToken.from_payload(payload)
        elif isinstance(payload, dict) and payload.get("type") == IdentityToken.TYPE:
            token = IdentityToken.from_payload(payload)
        else:
            return None
        return token if token and token.user.is_active else None


class MembershipToken(WorkspaceToken):
    def __init__(self, membership: WorkspaceMembership):
        self.membership = membership
        super().__init__(membership.user, membership.workspace)

    def payload(self) -> str:
        return str(self.membership.access_token)

    @classmethod
    def from_payload(cls, payload: str) -> "MembershipToken | None":
        try:
            membership = WorkspaceMembership.objects.get(access_token=payload)
        except WorkspaceMembership.DoesNotExist:
            return None
        return cls(membership)


class IdentityToken(WorkspaceToken):
    TYPE = "identity"

    def payload(self) -> dict:
        return {
            "type": self.TYPE,
            "workspace_id": str(self.workspace.id),
            "user_id": str(self.user.id),
            "issued_at": int(time.time()),
        }

    @staticmethod
    def is_expired(issued_at) -> bool:
        if not isinstance(issued_at, int):
            return True
        age = time.time() - issued_at
        return age > settings.WORKSPACE_IDENTITY_TOKEN_EXPIRE_SECONDS

    @classmethod
    def from_payload(cls, payload: dict) -> "IdentityToken | None":
        if cls.is_expired(payload.get("issued_at")):
            return None
        try:
            user = User.objects.get(id=payload["user_id"])
        except (KeyError, User.DoesNotExist):
            return None
        workspace = (
            Workspace.objects.filter_for_user(user)
            .filter(id=payload.get("workspace_id"))
            .first()
        )
        return cls(user, workspace) if workspace else None
