from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.http import HttpRequest

from hexa.analytics.api import set_user_properties
from hexa.user_management.models import User


@receiver(user_logged_in, sender=User, dispatch_uid="user_logged_in_handler")
def user_logged_in_handler(sender: type, request: HttpRequest, user: User, **kwargs):
    set_user_properties(user)
