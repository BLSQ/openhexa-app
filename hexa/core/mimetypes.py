import mimetypes

# This module might prove useless in the future but we use it for testing purposes for now
# TODO: reevaluate


def guess_type(url: str, strict: bool = True):
    return mimetypes.guess_type(url, strict)


def guess_extension(type: str, strict: bool = True):
    return mimetypes.guess_extension(type, strict)
