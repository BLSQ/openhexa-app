from django import template
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from django.template.loader import get_template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="highlight", is_safe=True)
def code(code, lang):
    lexer = get_lexer_by_name(lang, stripall=True)
    formatter = HtmlFormatter()
    return highlight(code, lexer, formatter)


@register.simple_tag(name="highlight-file")
def code_file(filename, lang):
    t = get_template(filename)
    return mark_safe(code(t.render(), lang))
