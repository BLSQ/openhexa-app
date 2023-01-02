from django_otp import devices_for_user, user_has_device

USER_DEFAULT_DEVICE_ATTR_NAME = "_default_device"


def default_device(user):
    if hasattr(user, USER_DEFAULT_DEVICE_ATTR_NAME):
        return getattr(user, USER_DEFAULT_DEVICE_ATTR_NAME)
    for device in devices_for_user(user):
        if device.name == "default":
            setattr(user, USER_DEFAULT_DEVICE_ATTR_NAME, device)
            return device


def is_two_factor_available(user):
    return user.is_authenticated and user.has_feature_flag("two_factor")


def has_configured_two_factor(user):
    return is_two_factor_available(user) and user_has_device(user)
