from hexa.user_management.models import User


def create_server(principal: User):
    """Authenticated users can create notebook servers"""

    return principal.is_authenticated
