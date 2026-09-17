"""The "<provider>:<model>" ids models are named by.

Agents and settings name a model in one of two ways: a logical name ("haiku"),
which only means something once a provider backend resolves it, or such an id,
which pydantic-ai can act on as is. Parsing is what tells the two apart, so it
happens once, here, rather than through `":" in value` checks spread over the
call sites.
"""

from dataclasses import dataclass

SEPARATOR = ":"


@dataclass(frozen=True)
class ModelId:
    provider: str
    name: str

    @classmethod
    def parse(cls, value: object) -> "ModelId | None":
        """The id `value` spells out, or None if it is not one.

        Takes an `object` because the values it is handed come from JSON an
        operator wrote: "not an id" and "not even a string" are the same answer.
        """
        if not isinstance(value, str):
            return None
        provider, separator, name = value.partition(SEPARATOR)
        if not separator or not provider or not name:
            return None
        return cls(provider=provider, name=name)

    def __str__(self) -> str:
        return f"{self.provider}{SEPARATOR}{self.name}"


# What an agent or a setting asks for: a model id, or the name of a logical
# model the organization's backend still has to resolve.
ModelRequest = ModelId | str
