from typing import TypedDict


class UserMessagePayload(TypedDict):
    id: str
    content: str


class ConversationNamePayload(TypedDict):
    name: str


class TextDeltaPayload(TypedDict):
    delta: str


class ToolCallPayload(TypedDict):
    tool_call_id: str
    tool_name: str
    tool_args: dict


class ToolResultPayload(TypedDict):
    tool_call_id: str
    tool_name: str
    success: bool
    tool_output: object


class DonePayload(TypedDict):
    message_id: str
    name: str | None


class ErrorCode(str):
    AGENT_STUCK_IN_LOOP = "AGENT_STUCK_IN_LOOP"
    MAX_TOKENS_REACHED = "MAX_TOKENS_REACHED"
    UNEXPECTED_MODEL_BEHAVIOR = "UNEXPECTED_MODEL_BEHAVIOR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ErrorPayload(TypedDict):
    error_code: str
