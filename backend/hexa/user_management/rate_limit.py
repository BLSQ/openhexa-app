from django.http import HttpRequest


# Not called by our code: django-axes calls it on every authenticate(), as it is set
# as AXES_USERNAME_CALLABLE in config/settings/base.py.
def get_username(request: HttpRequest, credentials: dict) -> str | None:
    """The username django-axes locks out on (`AXES_USERNAME_CALLABLE`): our login
    authenticates by `email`, where axes would look for `username`.

    Lowercased because emails match case-insensitively at login: otherwise each casing
    of an email would get its own failure count, and changing the case would escape
    the lockout.
    """
    email = (credentials or {}).get("email")
    return email.lower() if email else None
