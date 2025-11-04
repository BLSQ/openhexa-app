from __future__ import annotations

import base64

from hexa.core.credentials import HexaCredentials
from hexa.pipelines import models


class PipelinesCredentials(HexaCredentials):
    """
    This class acts as a container for credentials to be provided to the pipelines component.
    Optional run_id and pipeline name to add application_name to the connection
    string for debugging purposes.
    """

    def __init__(
        self, pipeline: models.Pipeline, run_id: str = None, pipeline_name: str = None
    ):
        self.pipeline: models.Pipeline = pipeline
        self.run_id: str = run_id
        self.pipeline_name: str = pipeline_name
        self.env: dict[str, str] = {}
        self.files: dict[str, bytes] = {}

    @property
    def reference_id(self):
        return self.pipeline.id

    def update_env(self, env_dict):
        self.env.update(**env_dict)

    def to_dict(self):
        return {
            "env": self.env,
            "files": {k: base64.b64encode(v).decode() for k, v in self.files.items()},
        }
