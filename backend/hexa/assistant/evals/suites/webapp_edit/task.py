"""Run one edit-webapp case against the real agent and a real git server.

The test environment stubs the git client, but this agent reads and proposes
against a repository, so the suite swaps a client for the dev Forgejo back in
for the length of the run. Each run gets its own git organization, deleted
afterwards.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import patch

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import connections
from pydantic_evals import increment_eval_metric

from hexa.assistant.agents.edit_webapp_agent import EditWebappAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, ToolInvocation
from hexa.git.forgejo import ForgejoAPIError, ForgejoClient
from hexa.user_management.models import User
from hexa.webapps.models import GitWebapp, Webapp

from ...core import CONVERSATION_COST_METRIC
from ...fixtures import build_profile, webapp_files
from ..pipeline_create.task import (
    EVAL_CONVERSATION_NAME,
    _configure_ai,
    _conversation_cost,
    _final_text,
)
from .schemas import ProposedWebappVersion, WebappEditInput

logger = logging.getLogger(__name__)

PROPOSE_TOOL = "propose_webapp_version"
# Summed per run, so the report shows how often each tool was called.
TOOL_CALLS_METRIC_PREFIX = "calls_"


def _git_client() -> ForgejoClient:
    return ForgejoClient(
        url=settings.GIT_SERVER_URL,
        username=settings.GIT_SERVER_ADMIN_USERNAME,
        password=settings.GIT_SERVER_ADMIN_PASSWORD,
    )


@contextmanager
def git_server() -> Iterator[None]:
    """Route web app repositories to the real git server during the run.

    Only the mixin's client is swapped: organizations still get the stub, so the
    task provisions the one git organization it needs itself.
    """
    with patch("hexa.git.mixins.get_forgejo_client", return_value=_git_client()):
        yield


def _build_world(profile: str, webapp_slug: str) -> tuple[Conversation, GitWebapp]:
    user = User.objects.create_user(
        f"eval-{uuid.uuid4().hex[:12]}@openhexa.org", "password", is_superuser=True
    )
    world = build_profile(profile, user)
    _configure_ai(world)
    organization = world.workspace.organization
    # Forgejo caps organization names at 40 characters, which the fixture's
    # uniquely suffixed slug exceeds.
    organization.slug = f"eval-{uuid.uuid4().hex[:12]}"
    organization.save(update_fields=["slug"])
    _git_client().create_organization(organization.slug, organization.name)
    webapp = GitWebapp.create_if_has_perm(
        user,
        world.workspace,
        name=webapp_slug.replace("-", " ").title(),
        created_by=user,
        webapp_type=Webapp.WebappType.STATIC,
        files=[
            {"path": path, "content": content}
            for path, content in webapp_files(webapp_slug).items()
        ],
    )
    conversation = Conversation.objects.create_if_has_perm(
        user,
        world.workspace,
        instruction_set=InstructionSet.EDIT_WEBAPP,
        linked_object=webapp,
    )
    # Suppresses the title-generation agent, as in pipeline_create.
    conversation.name = EVAL_CONVERSATION_NAME
    conversation.save(update_fields=["name"])
    return conversation, webapp


def _drop_git_org(webapp: GitWebapp) -> None:
    """Delete the run's repository and organization from the dev git server.

    Best effort: a leftover organization is clutter, not a wrong result.
    """
    client = _git_client()
    org = webapp.git_org.slug
    for path in (f"/repos/{org}/{webapp.repository}", f"/orgs/{org}"):
        try:
            # GitClient has no delete: the app archives, it never deletes.
            client._request("DELETE", path)
        except ForgejoAPIError as exc:
            logger.warning("Could not delete %s from the git server: %s", path, exc)


def _harvest(conversation: Conversation) -> ProposedWebappVersion:
    invocations = list(
        ToolInvocation.objects.filter(message__conversation=conversation).order_by(
            "created_at"
        )
    )
    tool_calls = [inv.tool_name for inv in invocations]
    proposals = [inv for inv in invocations if inv.tool_name == PROPOSE_TOOL]
    accepted = [
        inv for inv in proposals if inv.success and isinstance(inv.tool_output, dict)
    ]
    common = {
        "final_text": _final_text(conversation),
        "tool_calls": tool_calls,
        "rejected_proposals": len(proposals) - len(accepted),
    }
    if not accepted:
        return ProposedWebappVersion(**common)

    output = accepted[-1].tool_output
    return ProposedWebappVersion(
        files={f["path"]: f["content"] for f in output.get("files", [])},
        deleted_paths=output.get("deleted_paths", []),
        commit_message=output.get("commit_message"),
        **common,
    )


def make_task():
    async def run_case(inputs: WebappEditInput) -> ProposedWebappVersion:
        conversation, webapp = await sync_to_async(_build_world)(
            inputs.fixture_profile, inputs.webapp
        )
        try:
            agent = await sync_to_async(EditWebappAgent)(conversation)
            async for _ in agent.run_stream(inputs.prompt):
                pass
            cost = await sync_to_async(_conversation_cost)(conversation)
            if cost is not None:
                increment_eval_metric(CONVERSATION_COST_METRIC, float(cost))
            result = await sync_to_async(_harvest)(conversation)
            for name in result.tool_calls:
                increment_eval_metric(f"{TOOL_CALLS_METRIC_PREFIX}{name}", 1)
            return result
        finally:
            await sync_to_async(_drop_git_org)(webapp)
            await sync_to_async(connections.close_all)()

    return run_case
