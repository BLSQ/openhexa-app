from django import template as django_template
from django.template.base import token_kwargs
from django.template.loader_tags import (
    ExtendsNode,
    TemplateSyntaxError,
    construct_relative_path,
)

register = django_template.Library()


class EmbedNode(ExtendsNode):
    """Node renderer for thr {% embed %} template tag.
    https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-the-renderer
    """

    must_be_first = False
    context_key = "embeds_context"

    def __init__(
        self, nodelist, embedded_name, extra_context=None, isolated_context=False
    ):
        self.extra_context = extra_context or {}
        self.isolated_context = isolated_context
        super().__init__(nodelist, embedded_name)

    def render(self, context):
        values = {
            name: var.resolve(context) for name, var in self.extra_context.items()
        }

        if self.isolated_context:
            return super().render(context.new(values))

        with context.push(**values):
            return super().render(context)


@register.tag("embed")
def do_embed(parser, token):
    """{% embed %} template tag.

    Usage:
    > {% embed 'section.html' %}
    >   {% block title %}<h1>Title</h1>{% endblock %}
    >   {% block content %}<p>Content</p>{% endblock %}
    > {% endembed %}
    """

    nodelist = parser.parse(("endembed",))
    parser.delete_first_token()

    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError(
            "%r tag takes at least one argument: the name of the template to "
            "be included." % bits[0]
        )
    options = {}
    remaining_bits = bits[2:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise TemplateSyntaxError(
                "The %r option was specified more " "than once." % option
            )
        if option == "with":
            value = token_kwargs(remaining_bits, parser, support_legacy=False)
            if not value:
                raise TemplateSyntaxError(
                    '"with" in %r tag needs at least ' "one keyword argument." % bits[0]
                )
        elif option == "only":
            value = True
        else:
            raise TemplateSyntaxError(
                "Unknown argument for %r tag: %r." % (bits[0], option)
            )
        options[option] = value
    isolated_context = options.get("only", False)
    namemap = options.get("with", {})
    bits[1] = construct_relative_path(parser.origin.template_name, bits[1])

    return EmbedNode(
        nodelist,
        parser.compile_filter(bits[1]),
        extra_context=namemap,
        isolated_context=isolated_context,
    )
