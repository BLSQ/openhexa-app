from ariadne import convert_camel_case_to_snake
from django import forms

from graphql.utils import convert_snake_to_camel_case


class GraphQLForm(forms.Form):
    def __init__(self, data=None, *args, **kwargs):
        # TODO: convert back the field name in the errors to CamelCase
        # TODO: provide an escape hatch for more flexible renaming
        data = {convert_camel_case_to_snake(k): v for k, v in data.items()}
        super().__init__(data, *args, **kwargs)

    @property
    def provided_fields(self):
        return [
            field_name for field_name in self.fields.keys() if field_name in self.data
        ]

    @property
    def graphql_errors(self):
        return [
            {"field": convert_snake_to_camel_case(k), "message": v}
            for k, v in self.errors.get_json_data().items()
        ]


class GraphQLMultipleChoiceField(forms.MultipleChoiceField):
    def __init__(self, key_name="id", *args, **kwargs):
        self.key_name = key_name
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        # TODO: ValueError/ValidationError if not a list of dict ? Still accept a list of int/str ?
        if not value:
            return []
        value = [x[self.key_name] for x in value]
        return super().to_python(value)


class GraphQLChoiceField(forms.ChoiceField):
    def __init__(self, key_name="id", *args, **kwargs):
        self.key_name = key_name
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        # TODO: ValueError/ValidationError if not a dict ? Still accept a single str/int ?
        return super().to_python(value[self.key_name])


class EmptyValue:
    pass
