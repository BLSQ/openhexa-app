from enum import IntEnum

from django.db import models


class HttpMethod(IntEnum):
    GET = 1
    POST = 2


HTTP_METHODS = {e.value: e.name.capitalize() for e in HttpMethod}


class Request(models.Model):
    """
    Model to save all hits against the app. Used to discover catalog usage,
    debug, used lang. UserId is not a foreign key for performance issue:
    don't generate a cascade when user deletion, an user can have a lot of
    Request (and integrity is not really important, we don't need to stalk
    a user, we just need to have a unique group by key).
    """

    id = models.BigAutoField(primary_key=True, editable=False)
    user_id = models.UUIDField()
    url = models.TextField()
    query_string = models.TextField(default="")
    method = models.IntegerField(choices=HTTP_METHODS.items())
    request_time = models.DateTimeField()
    response_status = models.IntegerField()
    response_content_length = models.IntegerField()
    response_time = models.DateTimeField()
    user_agent = models.TextField()
    user_lang = models.TextField()
    referer = models.TextField()

    class Meta:
        ordering = ["-response_time"]
