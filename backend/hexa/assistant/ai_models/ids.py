"""The "<provider>:<model>" ids models are named by.

Agents and settings name a model in one of two ways: a logical name ("haiku"),
which only means something once a provider backend resolves it; or an id,
which pydantic-ai can act on as is. Parsing is what tells the two apart,
so it happens once, here.
"""

from dataclasses import dataclass

SEPARATOR = ":"


@dataclass(frozen=True)
class ModelId:
    provider: str
    name: str
    # Where the model is served, for backends that serve each model from its own
    # region. Not part of the id: pydantic-ai knows nothing about it.
    region: str | None = None

    @classmethod
    def parse(cls, value: object) -> "ModelId | None":
        """The model id in `value`, or None if it is not one.

        Takes an `object` because the values come from a JSON
        and could be something other than a string.
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
