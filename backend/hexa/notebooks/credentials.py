import base64

from hexa.core.credentials import HexaCredentials


class NotebooksCredentials(HexaCredentials):
    """This class acts as a container for credentials to be provided to the notebooks component."""

    def __init__(self, user):
        self.user = user  # TODO: enforce user
        self.env: dict[str, str] = {}
        self.files: dict[str, bytes] = {}

    @property
    def authenticated(self):  # TODO: remove once the "credentials" views is removed
        return self.user.is_authenticated

    @property
    def reference_id(self):
        return self.user.id

    def update_env(self, env_dict):
        self.env.update(**env_dict)

    def to_dict(self):
        return {
            "username": self.user.email,  # TODO: remove
            "env": self.env,
            "files": {k: base64.b64encode(v).decode() for k, v in self.files.items()},
        }
