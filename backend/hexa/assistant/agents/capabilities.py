from dataclasses import dataclass

from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.settings import ModelSettings


@dataclass(kw_only=True)
class MaxTokens(AbstractCapability):
    max_tokens: int

    def get_model_settings(self) -> ModelSettings:
        return ModelSettings(max_tokens=self.max_tokens)
