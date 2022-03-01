from django import forms

from hexa.core.graphql import (
    EmptyValue,
    GraphQLChoiceField,
    GraphQLForm,
    GraphQLMultipleChoiceField,
)
from hexa.core.test import TestCase


class ConnectorS3Test(TestCase):
    def test_base_form(self):
        class TestForm(GraphQLForm):
            a = forms.CharField()

        form = TestForm({"a": "value a"})
        assert form.is_valid()
        assert form.cleaned_data["a"] == "value a"

        form = TestForm({})
        assert not form.is_valid()

    def test_missing_fields_form(self):
        class TestForm(GraphQLForm):
            a = forms.CharField(required=False)
            b = forms.CharField(required=False)

        form = TestForm({"a": "value a"})
        assert form.is_valid()
        assert form.cleaned_data["a"] == "value a"
        assert "b" not in form.cleaned_data

    def test_choice_field(self):
        class TestForm(GraphQLForm):
            a = GraphQLChoiceField(choices=[("1", "one"), ("2", "two")])

        form = TestForm({"a": {"id": "1", "description": "one"}})
        assert form.is_valid()
        assert form.cleaned_data["a"] == "1"

    def test_multiple_choice_field(self):
        class TestForm(GraphQLForm):
            a = GraphQLMultipleChoiceField(
                choices=[("1", "one"), ("2", "two"), ("3", "three")]
            )

        form = TestForm(
            {
                "a": [
                    {"id": "1", "description": "one"},
                    {"id": "2", "description": "two"},
                ]
            }
        )
        assert form.is_valid()
        assert form.cleaned_data["a"] == ["1", "2"]

    def test_empty_value(self):
        class TestForm(GraphQLForm):
            a = forms.CharField(required=False, min_length=3, empty_value=EmptyValue())

        form = TestForm({"a": "value a"})
        assert form.is_valid()

        form = TestForm({})
        assert form.is_valid()

        form = TestForm({"a": "b"})
        assert not form.is_valid()

        form = TestForm({"a": ""})
        assert not form.is_valid()
