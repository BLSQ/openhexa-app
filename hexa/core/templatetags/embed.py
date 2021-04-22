import uuid

from django import template as django_template
from django.template.base import Node
from django.template import loader_tags

register = django_template.Library()


class EmbedNode(Node):
    """Embedding a template is a lot like extending it, with a few differences:
    - The node list comes from the nodes found between {% embed %} and {% endembed %}
    - We override render() to take the "with" and "only" arguments into account, like for {% include %}
    """

    must_be_first = False

    def __init__(
        self, nodelist, embedded_name, extra_context=None, isolated_context=False
    ):
        self.nodelist = nodelist
        self.embedded_name = embedded_name
        self.extra_context = extra_context or {}
        self.isolated_context = isolated_context

    def render(self, context):
        values = {
            name: var.resolve(context) for name, var in self.extra_context.items()
        }

        # Create an extend node with the same origin and use it for rendering
        extends_node = loader_tags.ExtendsNode(self.nodelist, self.embedded_name)
        extends_node.origin = getattr(self, "origin")

        # We need to generate new context keys for the extends node (to avoid history issues) and temporarily override
        # the value of BLOCK_CONTEXT key (to allow the sample template to be rendered twice with different block
        # contexts)
        extends_node.context_key = f"embed_context_{uuid.uuid4()}"
        block_context_key_value = loader_tags.BLOCK_CONTEXT_KEY
        loader_tags.BLOCK_CONTEXT_KEY = f"block_context_{uuid.uuid4()}"

        if self.isolated_context:
            rendered_node = extends_node.render(context.new(values))
        else:
            with context.push(**values):
                rendered_node = extends_node.render(context)

        # Restore BLOCK_CONTEXT_KEY to its previous value
        loader_tags.BLOCK_CONTEXT_KEY = block_context_key_value

        return rendered_node


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

    # do_block() will raise an exception if it detects two blocks with the same name
    current_loaded_blocks = getattr(parser, "__loaded_blocks", [])
    setattr(parser, "__loaded_blocks", [])

    nodelist = parser.parse(("endembed",))
    parser.delete_first_token()

    # This is a bit of a hack, but it allows to benefit from the parsing done for the {% include %} tag
    # without duplicating code
    include_node = loader_tags.do_include(parser, token)

    # now we can reassign the __loaded_blocks to its previous value
    setattr(parser, "__loaded_blocks", current_loaded_blocks)

    return EmbedNode(
        nodelist,
        include_node.template,
        extra_context=include_node.extra_context,
        isolated_context=include_node.isolated_context,
    )
