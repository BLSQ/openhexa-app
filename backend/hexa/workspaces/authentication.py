import abc
import binascii
from logging import getLogger

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
    def from_payload(cls, payload: str | dict) -> "WorkspaceToken | None":
        """Rebuild a token from a signed payload, or ``None`` if it is not ours."""

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

        # The payload type identifies the token: dict -> identity, str -> membership.
        token_type = _TOKEN_TYPES_BY_PAYLOAD.get(type(payload))
        return token_type.from_payload(payload) if token_type else None


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
    def payload(self) -> dict:
        return {
            "workspace_id": str(self.workspace.id),
            "user_id": str(self.user.id),
        }

    @classmethod
    def from_payload(cls, payload: dict) -> "IdentityToken | None":
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


_TOKEN_TYPES_BY_PAYLOAD = {
    dict: IdentityToken,
    str: MembershipToken,
}
