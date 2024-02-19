import enum

from colorhash import ColorHash
from django import template as django_template
from django.template import TemplateSyntaxError

from hexa.core.models.behaviors import Status

register = django_template.Library()


class Colors(str, enum.Enum):
    GRAY = "gray"
    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"
    BLUE = "blue"
    WHITE = "white"
    TRANSPARENT = "transparent"


STATUS_MAPPINGS = {
    Status.UNKNOWN: Colors.GRAY,
    Status.SUCCESS: Colors.GREEN,
    Status.ERROR: Colors.RED,
    Status.PENDING: Colors.YELLOW,
}


@register.filter(name="status_color")
def status_color(with_status):
    """Maps OpenHEXA status (see WithStatus behaviours) to colors for our templates"""
    try:
        return STATUS_MAPPINGS[with_status.status].value
    except AttributeError:
        return STATUS_MAPPINGS[Status.UNKNOWN].value


class ColorVariant(str, enum.Enum):
    PRIMARY = "primary"
    NEUTRAL = "neutral"


COLORS = {
    ColorVariant.PRIMARY: {
        "border": f"{Colors.TRANSPARENT}",
        "text": f"{Colors.WHITE}",
        "bg": f"{Colors.BLUE}-600",
        "hover:bg": f"{Colors.BLUE}-700",
        "focus:ring": f"{Colors.BLUE}-500",
    },
    ColorVariant.NEUTRAL: {
        "border": f"{Colors.GRAY}-300",
        "text": f"{Colors.GRAY}-700",
        "bg": f"{Colors.WHITE}",
        "hover:bg": f"{Colors.GRAY}-50",
        "focus:ring": f"{Colors.BLUE}-500",
    },
}


@register.filter(name="color")
def color(variant, part):
    """Return the color to use for the specified variant (example: primary) and part (example: border)"""
    try:
        return COLORS[ColorVariant(variant)][part]
    except (KeyError, ValueError):
        raise TemplateSyntaxError(f'Invalid color variant "{variant}"')


@register.filter(name="hash_color")
def hash_color(value, mode="hex"):
    """Generates a deterministic color value for the provided string."""
    return getattr(ColorHash(value), mode)
