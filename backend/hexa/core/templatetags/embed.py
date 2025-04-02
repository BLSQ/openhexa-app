import string

from django import template as django_template
from django.template.base import Node, TextNode, token_kwargs
from django.template.exceptions import TemplateSyntaxError
from django.template.loader_tags import construct_relative_path

register = django_template.Library()


def is_valid_embedded_node(node):
    if isinstance(node, TextNode):
        return node.s.translate({ord(c): None for c in string.whitespace}) == ""
    elif isinstance(node, SlotNode):
        return True

    return False


SLOT_CONTEXT_KEY_PREFIX = "slot_context_"


class EmbedNode(Node):
    """Embedding a template is a lot like including it, with a few differences:
    - We accept a node list: the {% slot %} nodes found between {% embed %} and {% endembed %}
    - As slots can be overridden, we need to store slot values in the context
    """

    def __init__(self, template, nodelist, extra_context=None, isolated_context=False):
        self.template = template
        self.nodelist = nodelist
        self.extra_context = extra_context or {}
        self.isolated_context = isolated_context

    def render(self, context):
        """Heavily inspired/borrowed from IncludeNode.render()"""
        # Exact copy from IncludeNode.render()
        template = self.template.resolve(context)
        # Does this quack like a Template?
        if not callable(getattr(template, "render", None)):
            # If not, try the cache and select_template().
            template_name = template or ()
            if isinstance(template_name, str):
                template_name = (template_name,)
            else:
                template_name = tuple(template_name)
            cache = context.render_context.dicts[0].setdefault(self, {})
            template = cache.get(template_name)
            if template is None:
                template = context.template.engine.select_template(template_name)
                cache[template_name] = template
        # Use the base.Template of a backends.django.Template.
        elif hasattr(template, "template"):
            template = template.template
        values = {
            name: var.resolve(context) for name, var in self.extra_context.items()
        }
        # End exact copy from IncludeNode.render()

        # First, make sure that we only have valid slot nodes in the node list or empty text nodes as children
        try:
            invalid_node = next(
                n for n in self.nodelist if not (is_valid_embedded_node(n))
            )

            raise TemplateSyntaxError(
                'Invalid node "%s" found within the embed tag (only "Slot" nodes are allowed)'
                % invalid_node.__class__.__name__
            )
        except StopIteration:
            slot_nodes = [n for n in self.nodelist if isinstance(n, SlotNode)]

        # Finally, render the node, taking isolated_context into account
        # (This is similar to IncludeNode.render() but we also need to store overridden slot values in th context)
        embedded_context = context.new() if self.isolated_context else context
        with embedded_context.push(values):
            slot_values = {
                SLOT_CONTEXT_KEY_PREFIX + n.name: n.render(embedded_context)
                for n in slot_nodes
            }
            with context.push(**slot_values):
                return template.render(context)


class SlotNode(Node):
    """Slot nodes are simple nodes meant to be defined in embedded templates, and overridden at embed time."""

    def __init__(self, name, nodelist):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        # If slot has been overridden, fetch its rendered value from the context
        if SLOT_CONTEXT_KEY_PREFIX + self.name in context:
            return context[SLOT_CONTEXT_KEY_PREFIX + self.name]

        # Otherwise, render default slot content
        return self.nodelist.render(context)


@register.tag("embed")
def do_embed(parser, token):
    """{% embed %} template tag. Allows to include a template and optionally override its slots, in a similar fashion
    to block tags in extended templates.

    Example::

        {% embed 'section.html' %}
            {% slot title %}<h1>Title</h1>{% endslot %}
            {% slot content %}<p>Content</p>{% endslot %}
        {% endembed %}

    You may use the ``only`` argument and keyword arguments using ``with`` like when using ``{% include %}``
    """
    # Exact copy from do_include_node()
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
                f"Unknown argument for {bits[0]!r} tag: {option!r}."
            )
        options[option] = value
    isolated_context = options.get("only", False)
    namemap = options.get("with", {})
    bits[1] = construct_relative_path(parser.origin.template_name, bits[1])
    # End exact copy from do_include_node()

    nodelist = parser.parse(("endembed",))
    parser.delete_first_token()

    return EmbedNode(
        parser.compile_filter(bits[1]),
        nodelist,
        extra_context=namemap,
        isolated_context=isolated_context,
    )


@register.tag("slot")
def do_slot(parser, token):
    """{% slot %} template tag.

    Example::

        {% embed 'section.html' %}
            {% slot title %}<h1>Title</h1>{% endslot %}
            {% slot content %}<p>Content</p>{% endslot %}
        {% endembed %}
    """
    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()

    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError(
            "%r tag takes at least one argument: the name of the template to "
            "be embedded." % bits[0]
        )

    return SlotNode(bits[1], nodelist)
