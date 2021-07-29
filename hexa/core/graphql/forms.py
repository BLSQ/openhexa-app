import stringcase
from ariadne import convert_camel_case_to_snake
from django import forms


class GraphQLForm(forms.Form):
    def __init__(self, data=None, *args, **kwargs):
        # TODO: convert back the field name in the errors to CamelCase
        # TODO: provide an escape hatch for more flexible renaming
        data = {convert_camel_case_to_snake(k): v for k, v in data.items()}
        super().__init__(data, *args, **kwargs)
        for field_name in self.base_fields.keys():
            if field_name not in data.keys() and not self.fields[field_name].required:
                self.fields.pop(field_name)

    @property
    def graphql_errors(self):
        errors = []
        for field_name, error_list in self.errors.get_json_data().items():
            for error in error_list:
                errors.append(
                    {
                        "field": stringcase.camelcase(field_name),
                        "message": error["message"],
                        "code": error["code"],
                    }
                )

        return errors


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
    """
    Can be used in forms.CharField like `CharField(required=False, min_length=3, empty_value=EmptyValue())`.
    This is useful to force the min_length validator to trigger is you send it an empty string.
    without the `empty_value=EmptyValue` and when `required=False`.

    Technical explanation: in `.run_validators()` (inherited from Field), the validators are short circuited
    when `value in self.empty_values` evaluates to True and `empty_value=''` for CharField so the value `''`
    (the empty string) bypasses all validation.

    Deeper technical explanation: this is needed only when `required=False` because otherwise `Field.validate()`
    raises a Validation error when the field value equals to `empty_value`.

    "We need to go deeper" technical explanation: by setting `empty_value=EmptyValue`, there is no chance that
    the field value will ever be equal to EmptyValue.
    """

    def __eq__(self, other):
        return False

    def __len__(self):
        return 0
