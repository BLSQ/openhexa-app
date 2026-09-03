import io
import json
import zipfile

from asgiref.sync import async_to_sync
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, DeltaToolCall, FunctionModel

from hexa.assistant.agents.base import AgentModels, BaseAgent
from hexa.assistant.model_builder import BuiltModel


def run_agent(agent: BaseAgent, message: str) -> None:
    async def _consume():
        async for _ in agent.run_stream(message):
            pass

    async_to_sync(_consume)()


def _fake_tool(arg: str) -> dict:
    return {"result": arg}


def _failing_tool(arg: str) -> dict:
    return {"errors": ["Something went wrong"]}


class _AgentWithFakeTool(BaseAgent):
    tools = [_fake_tool]


class _AgentWithFailingTool(BaseAgent):
    tools = [_failing_tool]


def _make_tool_call_model(tool_name: str, tool_args: dict) -> FunctionModel:
    calls = []

    def func(messages: list, agent_info: AgentInfo) -> ModelResponse:
        calls.append(1)
        if len(calls) == 1:
            return ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name=tool_name,
                        args=tool_args,
                        tool_call_id="call-test-001",
                    )
                ]
            )
        return ModelResponse(parts=[TextPart(content="Done.")])

    stream_calls = []

    async def stream_func(messages, agent_info):
        stream_calls.append(1)
        if len(stream_calls) == 1:
            yield {
                0: DeltaToolCall(
                    name=tool_name,
                    json_args=json.dumps(tool_args),
                    tool_call_id="call-test-001",
                )
            }
        else:
            yield "Done."

    return FunctionModel(func, stream_function=stream_func)


def make_built_model(test_model, api_name: str = "test") -> BuiltModel:
    return BuiltModel(model=test_model, api_name=api_name, provider_id="test")


def make_models(test_model, api_name: str = "test") -> AgentModels:
    """Run the main agent and its utility agents on one test model."""
    built = make_built_model(test_model, api_name)
    return AgentModels(main=built, utility=built)


def _make_truncated_tool_call_model(tool_name: str) -> FunctionModel:
    """Returns a model that yields a tool call with truncated (invalid) JSON args."""
    stream_calls = []

    async def stream_func(messages, agent_info):
        stream_calls.append(1)
        yield {
            0: DeltaToolCall(
                name=tool_name,
                json_args='{"arg": "trun',  # deliberately truncated
                tool_call_id="call-truncated-001",
            )
        }

    return FunctionModel(stream_function=stream_func)


def _make_zipfile(*files: tuple[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files:
            zf.writestr(name, content)
    return buf.getvalue()


def _make_naming_model(*titles: str) -> FunctionModel:
    """Model whose non-streamed calls return `titles` in order, repeating the last one.

    Only the naming agent issues non-streamed requests, so the counter tracks its
    attempts alone; the main agent is served by `stream_function`.
    """
    calls = []

    def func(messages: list, agent_info: AgentInfo) -> ModelResponse:
        index = min(len(calls), len(titles) - 1)
        calls.append(1)
        return ModelResponse(parts=[TextPart(content=titles[index])])

    async def stream_func(messages, agent_info):
        yield "Reply"

    return FunctionModel(func, stream_function=stream_func)
