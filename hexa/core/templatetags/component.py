from django import template as django_template
from django.template.base import Node, TextNode
from django.template import loader_tags, TemplateSyntaxError
from django.template.loader_tags import IncludeNode

register = django_template.Library()


class ComponentNode(IncludeNode):
    """Embedding a template is a lot like extending it, with a few differences:
    - The node list comes from the nodes found between {% embed %} and {% endembed %}
    - We override render() to take the "with" and "only" arguments into account, like for {% include %}
    """

    def __init__(self, nodelist, *args, **kwargs):
        self.nodelist = nodelist
        super().__init__(*args, **kwargs)

    def render(self, context):
        """Heavily inspired/borrowed from IncludeNode.render()"""

        try:
            invalid_node = next(
                n
                for n in self.nodelist
                if not (isinstance(n, TextNode) or isinstance(n, SlotNode))
            )

            raise TemplateSyntaxError(
                'Invalid node "%s" found within the component tag (only "Slot" nodes are allowed)'
                % invalid_node.__class__.__name__
            )
        except StopIteration:
            pass

        slot_nodes = [n for n in self.nodelist if isinstance(n, SlotNode)]
        with context.push({n.name: n.render(context) for n in slot_nodes}):
            return super().render(context)


class SlotNode(Node):
    """Embedding a template is a lot like extending it, with a few differences:
    - The node list comes from the nodes found between {% embed %} and {% endembed %}
    - We override render() to take the "with" and "only" arguments into account, like for {% include %}
    """

    def __init__(self, name, nodelist):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        if self.name in context:
            return context[self.name]

        return self.nodelist.render(context)


@register.tag("slot")
def do_slot(parser, token):
    """{% slot %} template tag.

    Example::

        {% component 'section.html' %}
            {% slot title %}<h1>Title</h1>{% endslot %}
            {% slot content %}<p>Content</p>{% endslot %}
        {% endcomponent %}
    """

    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()

    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError(
            "%r tag takes at least one argument: the name of the template to "
            "be used as component." % bits[B0]
        )

    return SlotNode(bits[1], nodelist)


@register.tag("component")
def do_component(parser, token):
    """{% component %} template tag.

    Example::

        {% component 'section.html' %}
            {% slot title %}<h1>Title</h1>{% endslot %}
            {% slot content %}<p>Content</p>{% endslot %}
        {% endcomponent %}

    You may use the ``only`` argument and keyword arguments using ``with`` like when using ``{% include %}``
    """

    nodelist = parser.parse(("endcomponent",))
    parser.delete_first_token()

    # This is a bit of a hack, but it allows to benefit from the parsing done for the {% include %} tag
    # without duplicating code
    include_node = loader_tags.do_include(parser, token)

    return ComponentNode(
        nodelist,
        include_node.template,
        extra_context=include_node.extra_context,
        isolated_context=include_node.isolated_context,
    )
