from django.apps import AppConfig

from hexa.plugins.app import CoreAppConfig


class CommentsConfig(AppConfig, CoreAppConfig):
    name = "hexa.comments"
    label = "comments"
