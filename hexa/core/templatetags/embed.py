from django import template as django_template
from django.template.loader_tags import (
    ExtendsNode,
    do_include,
)

register = django_template.Library()


class EmbedNode(ExtendsNode):
    """Embedding a template is a lot like extending it, with a few differences:
    - The node list comes from the nodes found between {% embed %} and {% endembed %}
    - We override render() to take the "with" and "only" arguments into account, like for {% include %}
    """

    must_be_first = False
    context_key = "embed_context"

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

    Example::

        {% embed 'section.html' %}
            {% block title %}<h1>Title</h1>{% endblock %}
            {% block content %}<p>Content</p>{% endblock %}
        {% endembed %}

    You may use the ``only`` argument and keyword arguments using ``with`` like when using ``{% include %}``
    """

    nodelist = parser.parse(("endembed",))
    parser.delete_first_token()

    # This is a bit of a hack, but it allows to benefit from the parsing done for the {% include %} tag
    # without dulicating code
    include_node = do_include(parser, token)

    return EmbedNode(
        nodelist,
        include_node.template,
        extra_context=include_node.extra_context,
        isolated_context=include_node.isolated_context,
    )
