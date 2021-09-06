class WithStatus:
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"

    @property
    def status(self):
        raise NotImplementedError(
            "Classes having the WithStatus behavior should implement status()"
        )
