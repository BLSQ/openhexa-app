from abc import ABC, abstractmethod


class HexaCredentials(ABC):
    """The HexaCredentials class acts as a interface to implement a container for credentials"""

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
