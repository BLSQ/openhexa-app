import functools
import typing

from django.http import HttpRequest


def do_not_track(view: typing.Callable) -> typing.Callable:
    """View decorator to disable tracking"""

    @functools.wraps(view)
    def untracked_view(request: HttpRequest, *args, **kwargs):
        request.META["HEXA_DO_NOT_TRACK"] = "true"

        return view(request, *args, **kwargs)

    return untracked_view
