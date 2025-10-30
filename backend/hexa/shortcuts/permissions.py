from hexa.user_management.models import User


def create_shortcut(principal: User, workspace):
    """Check if user can create shortcuts in a workspace"""
    return workspace.members.filter(id=principal.id).exists()


def delete_shortcut(principal: User, shortcut):
    """Check if user can delete a shortcut (only their own)"""
    return shortcut.user == principal
