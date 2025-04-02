import enum

from django import template as django_template
from django.template import TemplateSyntaxError

register = django_template.Library()


class SizeVariant(str, enum.Enum):
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"


SIZES = {
    SizeVariant.XS: {"px": "2.5", "py": "1.5", "text": "xs"},
    SizeVariant.SM: {"px": "3", "py": "2", "text": "sm"},
}


@register.filter(name="size")
def size(variant, part):
    """Return the size to use for the specified variant (example: sm) and part (example: px)"""
    try:
        return SIZES[SizeVariant(variant)][part]
    except (KeyError, ValueError):
        raise TemplateSyntaxError(f'Invalid size variant "{variant}"')
