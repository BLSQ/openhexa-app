from django import template
from django.contrib import messages

register = template.Library()


@register.filter(name="level_to_color", is_safe=True)
def level_to_color(level):
    """Maps a django messages level to a tailwind base color"""
    # Ensure the colors from here are up to date with hexa/templates/partials/messages.html
    return {
        messages.INFO: "blue",
        messages.SUCCESS: "green",
        messages.WARNING: "orange",
        messages.ERROR: "red",
    }[level]
