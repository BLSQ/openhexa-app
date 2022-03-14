import base64
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hexa.pipelines.models import Pipeline


class PipelinesConfiguration:
    """This class acts as a container for credentials to be provided to the pipelines component."""

    def __init__(self, pipeline: "Pipeline"):
        self.pipeline: "Pipeline" = pipeline
        self.env: dict[str, str] = {}
        self.files: dict[str, bytes] = {}
        self.connectors_configuration: dict[str, dict[str, str]] = {}

    def to_dict(self):
        return {
            "env": self.env,
            "files": {k: base64.b64encode(v).decode() for k, v in self.files.items()},
        }
