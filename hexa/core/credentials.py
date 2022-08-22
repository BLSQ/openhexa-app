from abc import ABC, abstractmethod

import hexa.core.models
from hexa.notebooks.credentials import NotebooksCredentials


class HexaCredentials(ABC):
    """This class acts as a interface to implement a container for credentials"""

    @property
    @abstractmethod
    def reference_id(self):
        pass

    @abstractmethod
    def update_env(self, env_dict):
        pass

    @abstractmethod
    def to_dict(self):
        pass


def custom_credentials(credentials: NotebooksCredentials):

    env = hexa.core.models.Credentials.objects.filter(user=credentials.user)

    if env:
        credentials.update_env(env)
