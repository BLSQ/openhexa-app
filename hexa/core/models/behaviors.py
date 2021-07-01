from django.db import models


class WithIndex(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.index()

    @property
    def index_type(self):  # TODO: remove
        raise NotImplementedError(
            "Each indexable model should implement the index_type() property"
        )

    def index(self):
        raise NotImplementedError(
            "Each indexable model should implement the index() method"
        )


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


class WithSync(models.Model):
    class Meta:
        abstract = True

    last_synced_at = models.DateTimeField(null=True, blank=True)

    def sync(self, user):
        raise NotImplementedError(
            "Classes having the WithSync behavior should implement sync()"
        )
