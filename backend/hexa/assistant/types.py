from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter


class TextSegment(BaseModel):
    type: Literal["text"] = "text"
    content: str


class ToolSegment(BaseModel):
    type: Literal["tool"] = "tool"
    tool_call_id: str


MessageSegment = Annotated[Union[TextSegment, ToolSegment], Field(discriminator="type")]
MessageSegmentAdapter: TypeAdapter[list[MessageSegment]] = TypeAdapter(
    list[MessageSegment]
)
