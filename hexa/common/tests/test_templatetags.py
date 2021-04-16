import pathlib
import string
from django.test import SimpleTestCase
from django.template import Context, Template, Engine

ENGINE = Engine.get_default()
ENGINE.dirs.append(pathlib.Path(__file__).parent.absolute() / pathlib.Path("templates"))


def remove_whitespace(original_string):
    return original_string.translate(({ord(c): None for c in string.whitespace}))


class TemplatetagsTest(SimpleTestCase):
    def assertTemplateContentEqual(self, first, second):
        return self.assertEqual(remove_whitespace(first), remove_whitespace(second))

    def test_embed_simple(self):
        context = Context({"title": "Context Title"})
        template_to_render = Template(
            """
            {% load embed %}
            {% embed "section.html" %}
                {% block title %}<h1>{{ title }}</h1>{% endblock %}
                {% block content %}<p>Content</p>{% endblock %}
            {% endembed %}
            """,
            engine=ENGINE,
        )
        rendered_template = template_to_render.render(context)
        self.assertTemplateContentEqual(
            """
            <div>
                <h1>Context Title</h1>
                <p>Content</p>
            </div>
            """,
            rendered_template,
        )

    def test_embed_isolated(self):
        context = Context({"extra_string": "extra string"})
        template_to_render = Template(
            """
            {% load embed %}
            {% embed "section.html" only %}
                {% block title %}<h1>Title</h1>{% endblock %}
                {% block content %}<p>Content{{ extra_string }}</p>{% endblock %}
            {% endembed %}
            """,
            engine=ENGINE,
        )
        rendered_template = template_to_render.render(context)
        self.assertTemplateContentEqual(
            """
            <div>
                <h1>Title</h1>
                <p>Content</p>
            </div>
            """,
            rendered_template,
        )

    def test_embed_extra_context(self):
        template_to_render = Template(
            """
            {% load embed %}
            {% embed "section.html" with title="Context Title" %}
                {% block title %}<h1>{{ title }}</h1>{% endblock %}
                {% block content %}<p>Content</p>{% endblock %}
            {% endembed %}
            """,
            engine=ENGINE,
        )
        rendered_template = template_to_render.render(Context())
        self.assertTemplateContentEqual(
            """
            <div>
                <h1>Context Title</h1>
                <p>Content</p>
            </div>
            """,
            rendered_template,
        )
