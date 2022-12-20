from hexa.user_management.models import User


def create_workspace(principal: User):
    """Only superusers can create a workspace"""
    return principal.is_superuser
