from django_otp import devices_for_user, user_has_device

USER_DEFAULT_DEVICE_ATTR_NAME = "_default_device"
DEVICE_DEFAULT_NAME = "default"


def default_device(user, confirmed=True):
    """
    confirmed: Pass None to get all devices
    """
    if hasattr(user, USER_DEFAULT_DEVICE_ATTR_NAME):
        return getattr(user, USER_DEFAULT_DEVICE_ATTR_NAME)
    for device in devices_for_user(user, confirmed=confirmed):
        if device.name == DEVICE_DEFAULT_NAME:
            setattr(user, USER_DEFAULT_DEVICE_ATTR_NAME, device)
            return device


def is_two_factor_available(user):
    return user.is_authenticated and user.has_feature_flag("two_factor")


def has_configured_two_factor(user):
    return is_two_factor_available(user) and user_has_device(user)
