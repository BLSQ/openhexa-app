from hexa.user_management.models import User

from .models import Collection


def create_collection(principal: User):
    """Collections can be created by anyone"""

    return principal.is_authenticated


def update_collection(principal: User, collection: Collection):
    """Only the author of the collection can update it"""

    return collection.author == principal


def delete_collection(principal: User, collection: Collection):
    """Only the author of the collection can delete it"""

    return collection.author == principal
