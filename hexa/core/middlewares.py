from django.http import HttpRequest


def set_remote_addr_from_forwarded_for(get_response):
    """Set the REMOTE_ADDR from the HTTP_X_FORWARDED_FOR header."""

    def middleware(request: HttpRequest):
        try:
            real_ip = request.META["HTTP_X_FORWARDED_FOR"]
        except KeyError:
            pass
        else:
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
            # Take just the first one.
            real_ip = real_ip.split(",")[0]
            request.META["REMOTE_ADDR"] = real_ip

        return get_response(request)

    return middleware
