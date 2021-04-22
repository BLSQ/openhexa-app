import string
from django import template as django_template
from django.template.base import Node, TextNode, token_kwargs
from django.template.exceptions import TemplateSyntaxError
from django.template.loader_tags import IncludeNode, construct_relative_path

register = django_template.Library()


def is_valid_embedded_node(node):
    if isinstance(node, TextNode):
        return node.s.translate(({ord(c): None for c in string.whitespace})) == ""
    elif isinstance(node, SlotNode):
        return True

    return False


class EmbedNode(Node):
    """Embedding a template is a lot like including it, with a few differences:
    - We accept a node list: the {% slot %} nodes found between {% embed %} and {% endembed %}
    - We override render() to take the "with" and "only" arguments into account, like for {% include %}
    """

    def __init__(self, template, nodelist, extra_context=None, isolated_context=False):
        self.template = template
        self.nodelist = nodelist
        self.extra_context = extra_context or {}
        self.isolated_context = isolated_context

    def render(self, context):
        """Heavily inspired/borrowed from IncludeNode.render()"""

        # Copy from IncludeNode.render()
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
        # End copy from IncludeNode.render()

        # First, make sure that we only have empty text nodes or valid slot nodes in the node list
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

        # Finally, render the node, taking isolated_context into account ("only" arg)
        # (This is similar to IncludeNode.render() but we also need to store overriden slot values in th context)
        if self.isolated_context:
            isolated_context = context.new(values)
            slot_values = {n.name: n.render(isolated_context) for n in slot_nodes}
            with isolated_context.push(slot_values):
                return template.render(isolated_context)
        else:
            with context.push({**values}):
                slot_values = {n.name: n.render(context) for n in slot_nodes}
                with context.push(**slot_values):
                    return template.render(context)


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

    nodelist = parser.parse(("endembed",))
    parser.delete_first_token()

    # Copy from do_include_node()
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
    # End copy from do_include_node()

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
