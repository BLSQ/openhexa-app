from django.db.models.signals import post_save
from django.dispatch import receiver

from hexa.user_management.models import AiSettings, User


@receiver(post_save, sender=User)
def create_ai_settings(sender, instance: User, created: bool, **kwargs):
    """
    Create AI settings when a new user is created.
    """
    if created:
        AiSettings.objects.create(user=instance)
