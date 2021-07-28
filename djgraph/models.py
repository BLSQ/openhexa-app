from django import forms

from djgraph.forms import GraphQLForm


class GraphQLModelForm(GraphQLForm):
    def __init__(self, data=None, instance=None, *args, **kwargs):
        if instance is None:
            # TODO: implement instance creation
            raise NotImplementedError("GraphQLForm must be given an instance")

        self.instance = instance
        super().__init__(data, *args, **kwargs)

    def save(self):
        # TODO: make GraphQLForm.save() behave like ModelForm.save() with regards to the
        # TODO: validation, clean, full_clean, ...
        # TODO: where do we handle validation looking at multiple fields at the time ?
        # HINT: look at _post_clean()
        for field_name in self.fields:
            # TODO: make a check on the model field (is a M2M or not) and not on the form field
            # TODO: split model update and M2M update like in the ModelForm
            # TODO: Warn if we are setattr on something that is not a model field
            if isinstance(self.fields[field_name], forms.ModelMultipleChoiceField):
                getattr(self.instance, field_name).set(self.cleaned_data[field_name])
            else:
                setattr(self.instance, field_name, self.cleaned_data[field_name])

        self.instance.save()
        return self.instance


class GraphQLModelChoiceField(forms.ModelChoiceField):
    def to_python(self, value):
        # TODO: ValueError/ValidationError if not a dict ? Still accept a single id as int/str ?
        if isinstance(value, dict):
            value = value["id"]
        return super().to_python(value)


class GraphQLModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    # TODO: ValueError/ValidationError if not a list of dict ? Still accept a list of int/str ?
    def _check_values(self, value):
        value = [x["id"] for x in value if isinstance(x, dict)]
        return super()._check_values(value)
