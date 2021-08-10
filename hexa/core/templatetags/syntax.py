from django import template
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from django.template.loader import get_template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="highlight", is_safe=True)
def highlight_code(code, lang):
    lexer = get_lexer_by_name(lang, stripall=True)
    formatter = HtmlFormatter()
    return highlight(code, lexer, formatter)


@register.simple_tag(takes_context=True, name="highlight-file")
def highlight_file(context, filename, lang):
    t = get_template(filename)
    context = dict(context.flatten())
    code = t.render(context)
    return mark_safe(highlight_code(code, lang))
