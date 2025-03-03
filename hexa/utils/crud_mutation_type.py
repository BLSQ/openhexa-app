from functools import wraps
from typing import Callable, Optional, Type

from ariadne import MutationType
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpRequest

from hexa.core.models import Base
from hexa.workspaces.models import Workspace


class CRUDMutationType(MutationType):
    def __init__(self, model: Type[Base]):
        super().__init__()
        self.model = model
        self.add_crud_operations()

    def add_crud_operations(self):
        self.set_field(f"create{self.model.__name__}", self.create())
        self.set_field(f"update{self.model.__name__}", self.update())
        self.set_field(f"delete{self.model.__name__}", self.delete())

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
            if pre_hook:
                pre_hook(request, input)
            try:
                instance = self.model.objects.create_if_has_perm(
                    request.user, workspace, **input
                )
                if post_hook:
                    post_hook(instance)
                return {
                    "success": True,
                    "errors": [],
                    self.model.__name__.lower(): instance,
                }
            except PermissionDenied:
                return {
                    "success": False,
                    "errors": ["PERMISSION_DENIED"],
                    self.model.__name__.lower(): None,
                }
            except IntegrityError:
                return {
                    "success": False,
                    "errors": ["ALREADY_EXISTS"],
                    self.model.__name__.lower(): None,
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
                instance = self.model.objects.filter_for_user(request.user).get(
                    id=input.pop("id")
                )
                if pre_hook:
                    pre_hook(instance, input)
                self.model.objects.update_if_has_perm(request.user, instance, **input)
                if post_hook:
                    post_hook(instance)
                return {
                    "success": True,
                    "errors": [],
                    self.model.__name__.lower(): instance,
                }
            except self.model.DoesNotExist:
                return {
                    "success": False,
                    "errors": [f"{self.model.__name__.upper()}_NOT_FOUND"],
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
                instance = self.model.objects.filter_for_user(request.user).get(
                    id=input["id"]
                )
                if pre_hook:
                    pre_hook(instance)
                self.model.objects.delete_if_has_perm(request.user, instance)
                if post_hook:
                    post_hook(instance)
                return {"success": True, "errors": []}
            except self.model.DoesNotExist:
                return {
                    "success": False,
                    "errors": [f"{self.model.__name__.upper()}_NOT_FOUND"],
                }
            except PermissionDenied:
                return {"success": False, "errors": ["PERMISSION_DENIED"]}

        return wrapper
