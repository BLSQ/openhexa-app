import datetime

from hexa.core.models import WithStatus
from hexa.core.models.behaviors import Status


class Activity(WithStatus):
    def __init__(
        self, status: str, occurred_at: datetime.datetime, description: Status
    ):
        self._status = status
        self.occurred_at = occurred_at
        self.description = description

    @property
    def status(self):
        return self._status
