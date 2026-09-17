"""Which model an organization runs, and how to reach it.

`AiModelBuilder` is the way in: it hands an agent the model it should run on,
built with credentials that organization can use. Behind it, `selection` decides
which model that is, `backends` supplies the credentials and `config` reads what
the deployment set in its environment.
"""

from hexa.assistant.ai_models.builder import AiModelBuilder
from hexa.assistant.ai_models.built_model import BuiltModel
from hexa.assistant.ai_models.ids import ModelId

__all__ = ["AiModelBuilder", "BuiltModel", "ModelId"]
