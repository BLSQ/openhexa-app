"""Run one create-pipeline case against the real agent.

Nothing is stubbed. The real CreatePipelineAgent, MCP tools and GraphQL
resolvers run against a workspace that exists only for the length of the run.
"""

from __future__ import annotations

import json
import uuid

from asgiref.sync import sync_to_async
from django.db import connections

from hexa.assistant.agents.create_pipeline_agent import CreatePipelineAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.user_management.models import AiSettings, User

from ...fixtures import EvalWorld, build_profile
from .schemas import PipelineCreateInput, ProposedPipeline

CREATE_TOOL = "create_pipeline"
EVAL_CONVERSATION_NAME = "eval run"


def _configure_ai(world: EvalWorld) -> None:
    """Point the fixture organization at the managed (Vertex) provider.

    Vertex is what production runs on, and it needs no API key: it authenticates
    with ambient Google credentials. Model and key stay null because
    AiModelBuilder ignores both for managed orgs and always resolves
    MANAGED_DEFAULT_MODEL.
    """
    AiSettings.objects.update_or_create(
        organization=world.workspace.organization,
        defaults={
            "enabled": True,
            "provider": AiSettings.Provider.MANAGED,
            "model": None,
            "api_key": None,
        },
    )


def _build_world(profile: str) -> tuple[EvalWorld, Conversation]:
    user = User.objects.create_user(
        f"eval-{uuid.uuid4().hex[:12]}@openhexa.org", "password", is_superuser=True
    )
    world = build_profile(profile, user)
    _configure_ai(world)
    conversation = Conversation.objects.create_if_has_perm(
        user, world.workspace, instruction_set=InstructionSet.CREATE_PIPELINE
    )
    # Naming the conversation up front suppresses the title-generation agent,
    # which run_stream only starts when `conversation.name is None`. It is a
    # second model round-trip per case that is not the thing under test, and
    # its usage is folded into the case's cost and request count.
    conversation.name = EVAL_CONVERSATION_NAME
    conversation.save(update_fields=["name"])
    return world, conversation


def _files_from_args(tool_input: dict) -> dict[str, str]:
    """Read the file set out of the agent's own create_pipeline arguments.

    Graded from what the agent sent rather than the stored PipelineVersion. If
    the call was rejected the arguments still show what it tried to build, and
    tier 0 fails the result on its own merits.
    """
    raw = tool_input.get("files_json")
    if not raw:
        return {}
    try:
        entries = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError):
        return {}
    if not isinstance(entries, list):
        return {}
    return {
        entry["path"]: entry.get("content", "")
        for entry in entries
        if isinstance(entry, dict) and entry.get("path")
    }


def _final_text(conversation: Conversation) -> str | None:
    """The agent's closing explanation, flattened out of its message segments.

    Message.content is a JSON list of text and tool segments, not a string, so
    the text parts are joined and the tool markers dropped.
    """
    content = (
        Message.objects.filter(conversation=conversation, role=Message.Role.ASSISTANT)
        .order_by("-created_at")
        .values_list("content", flat=True)
        .first()
    )
    if content is None:
        return None
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return None
    parts = [
        segment["content"]
        for segment in content
        if isinstance(segment, dict)
        and segment.get("type") == "text"
        and isinstance(segment.get("content"), str)
    ]
    return "\n".join(parts) or None


def _harvest(conversation: Conversation) -> ProposedPipeline:
    invocations = list(
        ToolInvocation.objects.filter(message__conversation=conversation).order_by(
            "created_at"
        )
    )
    tool_calls = [inv.tool_name for inv in invocations]

    created = next(
        (
            inv
            for inv in reversed(invocations)
            if inv.tool_name == CREATE_TOOL and inv.success
        ),
        None,
    )
    final_text = _final_text(conversation)

    if created is None:
        return ProposedPipeline(tool_calls=tool_calls, final_text=final_text)

    args = created.tool_input or {}
    return ProposedPipeline(
        name=args.get("name"),
        description=args.get("description"),
        functional_type=args.get("functional_type"),
        files=_files_from_args(args),
        final_text=final_text,
        tool_calls=tool_calls,
    )


def make_task():
    """Build the task callable pydantic-evals drives.

    Takes no configuration. The provider is always managed, and Vertex resolves
    the model itself.
    """

    async def run_case(inputs: PipelineCreateInput) -> ProposedPipeline:
        # A fresh world per run, not per case: repeats of the same case must not
        # see each other's pipelines, and the agent's tools read live from the DB.
        _, conversation = await sync_to_async(_build_world)(inputs.fixture_profile)
        try:
            agent = await sync_to_async(CreatePipelineAgent)(conversation)
            async for _ in agent.run_stream(inputs.prompt):
                pass
            return await sync_to_async(_harvest)(conversation)
        finally:
            # Closed on the same worker thread that opened them; a connection
            # left open here blocks DROP DATABASE at teardown.
            await sync_to_async(connections.close_all)()

    return run_case
