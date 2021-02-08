from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = "habari.auth"
    label = "habari_auth"  # avoid conflicts with base django auth

    verbose_name = "User management"
