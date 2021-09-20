from unittest.mock import Mock

from django import forms, test

from hexa.core.graphql import GraphQLModelChoiceField, GraphQLModelForm
from hexa.user_management.models import Organization


class ConnectorS3Test(test.TestCase):
    def test_base_form(self):
        class TestForm(GraphQLModelForm):
            a_b = forms.CharField()
            c = forms.CharField(required=False)

        instance = Mock()
        instance.c = "do not touch"
        form = TestForm({"aB": "value a"}, instance=instance)
        assert form.is_valid()

        assert form.save() is instance
        assert instance.save.called

        assert instance.a_b == "value a"
        assert instance.c == "do not touch"

    def test_choice(self):
        class TestForm(GraphQLModelForm):
            orga = GraphQLModelChoiceField(queryset=Organization.objects.all())

        o1 = Organization.objects.create(name="org1")
        o2 = Organization.objects.create(name="org2")

        instance = Mock()
        form = TestForm({"orga": {"id": o1.id, "name": "org1"}}, instance=instance)
        assert form.is_valid(), form.errors

        form.save()
        assert instance.orga == o1

    def test_bad_choice(self):
        class TestForm(GraphQLModelForm):
            owner_orga = GraphQLModelChoiceField(queryset=Organization.objects.all())

        o1 = Organization.objects.create(name="org1")

        instance = Mock()
        form = TestForm(
            {
                "ownerOrga": {
                    "id": "deadbeef-dead-beef-dead-beefdeadbeef",
                    "name": "non-existing",
                }
            },
            instance=instance,
        )
        assert not form.is_valid()
        assert form.graphql_errors == [
            {
                "field": "ownerOrga",
                "message": "Select a valid choice. That choice is not one of the available choices.",
                "code": "invalid_choice",
            }
        ]

    # def test_multi_choice(self):
    #     class TestForm(GraphQLModelForm):
    #         tags = GraphQLModelMultipleChoiceField(queryset=Tag.objects.all())
    #
    #     tag1 = Tag.objects.create(name="tag1")
    #     tag2 = Tag.objects.create(name="tag2")
    #     tag3 = Tag.objects.create(name="tag3")
    #
    #     instance = Mock()
    #     form = TestForm(
    #         {
    #             "tags": [
    #                 {"id": tag1.id, "name": "tag1"},
    #                 {"id": tag2.id, "name": "tag2"},
    #             ]
    #         },
    #         instance=instance,
    #     )
    #     assert form.is_valid(), form.errors
    #
    #     form.save()
    #     assert instance.tags.set.called
    #     self.assertQuerysetEqual(
    #         instance.tags.set.call_args.args[0], [tag1, tag2], ordered=False
    #     )
