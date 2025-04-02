import enum


class Status(enum.Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    TERMINATING = "TERMINATING"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class WithStatus:
    @property
    def status(self) -> Status:
        raise NotImplementedError(
            "Classes having the WithStatus behavior should implement status()"
        )
