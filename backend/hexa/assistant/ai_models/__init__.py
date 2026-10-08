"""Which model an organization runs, and how to reach it.

- `builder` is the way in: it hands an agent the model it to run on. Built with credentials from the organization.
- `selection` decides which model to pick
- `backends` supplies the credentials
- `config` reads what the deployment set in its environment
- `built_model` and `ids` are dataclasses to manage models information
"""

from hexa.assistant.ai_models.builder import AiModelBuilder
from hexa.assistant.ai_models.built_model import BuiltModel
from hexa.assistant.ai_models.ids import ModelId

__all__ = ["AiModelBuilder", "BuiltModel", "ModelId"]
