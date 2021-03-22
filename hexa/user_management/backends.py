from django.contrib.auth.backends import ModelBackend as BaseModelBackend


class ModelBackend(BaseModelBackend):
    """Custom permission backend that uses model methods to check for permissions."""

    def get_user_permissions(self, user_obj, obj=None):
        base_permissions = super().get_user_permissions(user_obj, obj)

        return base_permissions

    def get_group_permissions(self, user_obj, obj=None):
        base_permissions = super().get_group_permissions(user_obj, obj)

        return base_permissions

    def get_all_permissions(self, user_obj, obj=None):
        base_permissions = super().get_all_permissions(user_obj, obj)

        return base_permissions

    def has_perm(self, user_obj, perm, obj=None):
        base_has_perm = super().has_perm(user_obj, perm, obj)

        return base_has_perm

    def has_module_perms(self, user_obj, app_label):
        base_has_module_perms = super().has_module_perms(user_obj, app_label)

        return base_has_module_perms

    def with_perm(self, perm, is_active=True, include_superusers=True, obj=None):
        base_with_perm = super().with_perm(perm, is_active, include_superusers, obj)

        return base_with_perm
