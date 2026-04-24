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


class ToolResultPayload(TypedDict):
    tool_call_id: str
    tool_name: str
    success: bool
    tool_output: object


class DonePayload(TypedDict):
    message_id: str
    name: str | None


class ErrorPayload(TypedDict):
    message: str
