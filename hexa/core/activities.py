import datetime
import typing

from hexa.core.models import WithStatus
from hexa.core.models.behaviors import Status


class Activity(WithStatus):
    def __init__(
        self,
        *,
        status: Status,
        occurred_at: datetime.datetime,
        description: str,
        url: str
    ):
        self._status = status
        self.occurred_at = occurred_at
        self.description = description
        self.url = url

    @property
    def status(self):
        return self._status


class ActivityList:
    def __init__(self, items: typing.List[Activity] = []):
        self.items = items

    def __iter__(self):
        self.order_by("-occurred_at")
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, item):
        return self.items.__getitem__(item)

    def order_by(self, order_by: str):
        if order_by not in ["-occurred_at"]:
            raise ValueError("Only -occurred is supported")

        self.items = sorted(self.items, key=lambda a: a.occurred_at.timestamp())

    def __add__(self, other: "ActivityList"):
        return ActivityList(self.items + other.items)
