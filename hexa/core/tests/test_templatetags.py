import pathlib

from django.template import Context, Engine, Template
from django.test import SimpleTestCase

from hexa.core.string import remove_whitespace

ENGINE = Engine.get_default()
ENGINE.dirs.append(pathlib.Path(__file__).parent.absolute() / pathlib.Path("templates"))


class TemplatetagsTest(SimpleTestCase):
    def assertTemplateContentEqual(self, first, second):
        return self.assertEqual(remove_whitespace(first), remove_whitespace(second))

    def test_embed_simple(self):
        """Simplest case, two subsequent embeds on a template that does not extend anything"""
        context = Context(
            {"title_1": "First Embedded Title", "title_2": "Second Embedded Title"}
        )
        template_to_render = Template(
            """
            {% load embed %}
            {% embed "section.html" %}
                {% slot title %}{{ title_1 }}{% endslot %}
                {% slot content %}<p>Some content</p>{% endslot %}
            {% endembed %}
            {% embed "section.html" %}
                {% slot title %}{{ title_2 }}{% endslot %}
                {% slot content %}<p>Another content</p>{% endslot %}
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
        """Make sure that embed plays well with extends."""
        context = Context({"title": "Embedded Title"})
        template_to_render = Template(
            """
            {% extends "base.html" %}
            {% load embed %}
            {% block page_title %}Extended Title{% endblock %}
            {% block body %}
                {% embed "section.html" %}
                    {% slot title %}{{ title }}{% endslot %}
                    {% slot content %}<p>Content</p>{% endslot %}
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
        template_to_render = Template(
            """
            {% load embed %}
            {% embed "section.html" with title="Extra Title" only %}
                {% slot title %}Extra Title{% endslot %}
                {% slot content %}<p>Content{{ context_string }}</p>{% endslot %}
            {% endembed %}
            """,
            engine=ENGINE,
        )
        rendered_template = template_to_render.render(
            Context({"context_string": " (context string)"})
        )
        self.assertTemplateContentEqual(
            """
            <section>
                <h1>Extra Title</h1>
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
            {% embed "section.html" with title="Extra Title" %}
                {% slot title %}{{ title }}{% endslot %}
                {% slot content %}<p>Content{{ context_string }}</p>{% endslot content %}
            {% endembed %}
            """,
            engine=ENGINE,
        )
        rendered_template = template_to_render.render(
            Context({"context_string": " (context string)"})
        )
        self.assertTemplateContentEqual(
            """
            <section>
                <h1>Extra Title</h1>
                <div>
                    <p>Content (context string)</p>
                </div>
            </section>
            """,
            rendered_template,
        )
