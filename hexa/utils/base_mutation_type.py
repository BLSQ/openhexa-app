from functools import wraps
from typing import Callable, Optional

from ariadne import MutationType
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.http import HttpRequest

from hexa.core.models.base import BaseManager, BaseQuerySet
from hexa.workspaces.models import Workspace


class BaseMutationType(MutationType):
    def __init__(self, manager: BaseManager, query_set: BaseQuerySet):
        super().__init__()
        self.manager = manager
        self.model_name = manager.model.__name__
        self.query_set = query_set
        self.set_field(f"create{self.model_name}", self.create())
        self.set_field(f"update{self.model_name}", self.update())
        self.set_field(f"delete{self.model_name}", self.delete())

    def create(
        self, pre_hook: Optional[Callable] = None, post_hook: Optional[Callable] = None
    ):
        @wraps(self.create)
        def wrapper(_, info, **kwargs):
            request: HttpRequest = info.context["request"]
            input = kwargs["input"]
            workspace_slug = input.pop("workspace_slug")
            try:
                workspace = Workspace.objects.filter_for_user(request.user).get(
                    slug=workspace_slug
                )
            except Workspace.DoesNotExist:
                return {
                    "success": False,
                    "errors": ["WORKSPACE_NOT_FOUND"],
                }
            try:
                with transaction.atomic():
                    if pre_hook:
                        pre_hook(request, input)

                    input["workspace"] = workspace
                    instance = self.manager.create_if_has_perm(
                        request.user, workspace, **input
                    )

                    if post_hook:
                        post_hook(instance)
                return {
                    "success": True,
                    "errors": [],
                    self.model_name.lower(): instance,
                }
            except PermissionDenied:
                return {
                    "success": False,
                    "errors": ["PERMISSION_DENIED"],
                    self.model_name.lower(): None,
                }
            except IntegrityError:
                return {
                    "success": False,
                    "errors": ["ALREADY_EXISTS"],
                    self.model_name.lower(): None,
                }

        return wrapper

    def update(
        self, pre_hook: Optional[Callable] = None, post_hook: Optional[Callable] = None
    ):
        @wraps(self.update)
        def wrapper(_, info, **kwargs):
            request: HttpRequest = info.context["request"]
            input = kwargs["input"]
            try:
                instance = self.query_set.filter_for_user(request.user).get(
                    id=input.pop("id")
                )
                if pre_hook:
                    pre_hook(instance, input)
                self.manager.update_if_has_perm(request.user, instance, **input)
                if post_hook:
                    post_hook(instance)
                return {
                    "success": True,
                    "errors": [],
                    self.model_name.lower(): instance,
                }
            except self.manager.model.DoesNotExist:
                return {
                    "success": False,
                    "errors": [f"{self.model_name.upper()}_NOT_FOUND"],
                }
            except PermissionDenied:
                return {"success": False, "errors": ["PERMISSION_DENIED"]}

        return wrapper

    def delete(
        self, pre_hook: Optional[Callable] = None, post_hook: Optional[Callable] = None
    ):
        @wraps(self.delete)
        def wrapper(_, info, **kwargs):
            request: HttpRequest = info.context["request"]
            input = kwargs["input"]
            try:
                instance = self.query_set.filter_for_user(request.user).get(
                    id=input["id"]
                )
                if pre_hook:
                    pre_hook(instance)
                self.manager.delete_if_has_perm(request.user, instance)
                if post_hook:
                    post_hook(instance)
                return {"success": True, "errors": []}
            except self.manager.model.DoesNotExist:
                return {
                    "success": False,
                    "errors": [f"{self.model_name.upper()}_NOT_FOUND"],
                }
            except PermissionDenied:
                return {"success": False, "errors": ["PERMISSION_DENIED"]}

        return wrapper
