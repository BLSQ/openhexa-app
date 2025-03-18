from ariadne import MutationType
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpRequest

from hexa.core.models.base import BaseManager, BaseQuerySet
from hexa.workspaces.models import Workspace


class BaseWorkspaceMutationType(MutationType):
    def __init__(self, manager: BaseManager, query_set: BaseQuerySet):
        super().__init__()
        self.manager = manager
        self.model_name = manager.model.__name__
        self.query_set = query_set
        self.set_field(f"create{self.model_name}", self.create())
        self.set_field(f"update{self.model_name}", self.update())
        self.set_field(f"delete{self.model_name}", self.delete())

    def create(self):
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
                input["workspace"] = workspace
                self.pre_create(request, input)
                instance = self.perform_create(request, input, workspace)
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

    def update(self):
        def wrapper(_, info, **kwargs):
            request: HttpRequest = info.context["request"]
            input = kwargs["input"]
            try:
                instance = self.query_set.filter_for_user(request.user).get(
                    id=input.pop("id")
                )
                self.pre_update(request, instance, input)
                self.perform_update(request, instance, input)
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

    def delete(self):
        def wrapper(_, info, **kwargs):
            request: HttpRequest = info.context["request"]
            input = kwargs["input"]
            try:
                instance = self.query_set.filter_for_user(request.user).get(
                    id=input["id"]
                )
                self.pre_delete(request, instance)
                self.perform_delete(request, instance)
                return {"success": True, "errors": []}
            except self.manager.model.DoesNotExist:
                return {
                    "success": False,
                    "errors": [f"{self.model_name.upper()}_NOT_FOUND"],
                }
            except PermissionDenied:
                return {"success": False, "errors": ["PERMISSION_DENIED"]}

        return wrapper

    def perform_create(self, request: HttpRequest, input: dict, workspace: Workspace):
        return self.manager.create_if_has_perm(request.user, workspace, **input)

    def perform_update(self, request: HttpRequest, instance, input: dict):
        self.manager.update_if_has_perm(request.user, instance, **input)

    def perform_delete(self, request: HttpRequest, instance):
        self.manager.delete_if_has_perm(request.user, instance)

    def pre_create(self, request: HttpRequest, input: dict):
        pass

    def pre_update(self, request: HttpRequest, instance, input: dict):
        pass

    def pre_delete(self, request: HttpRequest, instance):
        pass
