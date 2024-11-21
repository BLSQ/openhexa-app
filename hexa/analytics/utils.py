from django.http import HttpRequest


def get_ip_address(request: HttpRequest) -> str:
    """Get the IP address from the request object."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META["REMOTE_ADDR"]
    return ip
