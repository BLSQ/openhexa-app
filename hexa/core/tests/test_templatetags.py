from django.test import SimpleTestCase
from django.template import Context, Template, Engine
import pathlib

from hexa.core.string import remove_whitespace

ENGINE = Engine.get_default()
ENGINE.dirs.append(pathlib.Path(__file__).parent.absolute() / pathlib.Path("templates"))


class TemplatetagsTest(SimpleTestCase):
    def assertTemplateContentEqual(self, first, second):
        return self.assertEqual(remove_whitespace(first), remove_whitespace(second))

    def test_embed_simple(self):
        """Simplest case, single embed on a template that does not extend anything"""

        context = Context(
            {"title_1": "First Embedded Title", "title_2": "Second Embedded Title"}
        )
        template_to_render = Template(
            """
            {% load embed %}
            {% embed "section.html" %}
                {% block title %}{{ title_1 }}{% endblock %}
                {% block content %}<p>Some content</p>{% endblock %}
            {% endembed %}
            {% embed "section.html" %}
                {% block title %}{{ title_2 }}{% endblock %}
                {% block content %}<p>Another content</p>{% endblock %}
            {% endembed %}
            """,
            engine=ENGINE,
        )
        rendered_template = template_to_render.render(context)
        self.assertTemplateContentEqual(
            """
            <section>
                <h1>First Embedded Title</h1>
                <div>
                    <p>Some content</p>
                </div>
            </section>
            <section>
                <h1>Second Embedded Title</h1>
                <div>
                    <p>Another content</p>
                </div>
            </section>
            """,
            rendered_template,
        )

    def test_embed_extends(self):
        """Make sure that embed does not conflict with extends."""

        context = Context({"title": "Embedded Title"})
        template_to_render = Template(
            """
            {% extends "base.html" %}
            {% load embed %}
            {% block page_title %}Extended Title{% endblock %}
            {% block body %}
                {% embed "section.html" %}
                    {% block title %}{{ title }}{% endblock %}
                {% block content %}<p>Content</p>{% endblock %}
            {% endembed %}
            {% endblock %}
            """,
            engine=ENGINE,
        )
        rendered_template = template_to_render.render(context)
        self.assertTemplateContentEqual(
            """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Extended Title</title>
            </head>
            <body>
                <section>
                    <h1>Embedded Title</h1>
                    <div>
                        <p>Content</p>
                    </div>
                </section>
            </body>
            </html>
            """,
            rendered_template,
        )

    def test_embed_isolated(self):
        context = Context({"extra_string": "extra string"})
        template_to_render = Template(
            """
            {% load embed %}
            {% embed "section.html" only %}
                {% block title %}Title{% endblock %}
                {% block content %}<p>Content{{ extra_string }}</p>{% endblock %}
            {% endembed %}
            """,
            engine=ENGINE,
        )
        rendered_template = template_to_render.render(context)
        self.assertTemplateContentEqual(
            """
            <section>
                <h1>Title</h1>
                <div>
                    <p>Content</p>
                </div>
            </section>
            """,
            rendered_template,
        )

    def test_embed_extra_context(self):
        template_to_render = Template(
            """
            {% load embed %}
            {% embed "section.html" with title="Context Title" %}
                {% block title %}{{ title }}{% endblock %}
                {% block content %}<p>Content</p>{% endblock %}
            {% endembed %}
            """,
            engine=ENGINE,
        )
        rendered_template = template_to_render.render(Context())
        self.assertTemplateContentEqual(
            """
            <section>
                <h1>Context Title</h1>
                <div>
                    <p>Content</p>
                </div>
            </section>
            """,
            rendered_template,
        )
