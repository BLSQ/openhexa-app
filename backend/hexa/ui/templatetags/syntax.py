from django import template
from django.template import Node, TemplateSyntaxError
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from markdown import markdown as to_markdown
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name

register = template.Library()


@register.filter(name="markdown", is_safe=True)
def highlight_markdown(code):
    return mark_safe(to_markdown(code))


@register.filter(name="highlight", is_safe=True)
def highlight_code(code, lang):
    lexer = get_lexer_by_name(lang, stripall=True)
    formatter = HtmlFormatter()
    return mark_safe(highlight(code, lexer, formatter))


@register.simple_tag(takes_context=True, name="highlight-file")
def highlight_file(context, filename, lang):
    t = get_template(filename)
    context = dict(context.flatten())
    code = t.render(context)
    return mark_safe(highlight_code(code, lang))


class HighlightNode(Node):
    def __init__(self, nodelist, lang):
        self.lang = lang
        self.nodelist = nodelist

    def render(self, context):
        return mark_safe(highlight_code(self.nodelist.render(context), self.lang))


@register.tag("highlight")
def highlight_block(parser, token):
    nodelist = parser.parse(("endhighlight",))
    parser.delete_first_token()

    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r tag takes a single 'language' argument" % bits[0])

    return HighlightNode(nodelist, bits[1])
