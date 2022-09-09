from hexa.user_management.models import User

from .models import Collection, CollectionElement


def create_collection(principal: User):
    """Collections can be created by anyone"""

    return principal.is_authenticated


def update_collection(principal: User, collection: Collection):
    """Only the author of the collection can update it"""

    return principal.is_authenticated


def delete_collection(principal: User, collection: Collection):
    """Only the author of the collection can delete it"""

    return principal.is_authenticated


def create_collection_element(principal: User, collection: Collection):
    """Every authenticated user can add items to collections"""

    return principal.is_authenticated


def delete_collection_element(principal: User, element: CollectionElement):
    """Every authenticated user can delete items to collections"""

    return principal.is_authenticated
