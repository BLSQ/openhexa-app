from django.core.validators import RegexValidator
from django.forms import TextInput
from django_ltree.fields import PathField as BasePathField
from django_ltree.fields import PathFormField as BasePathFormField

# we need to replace the django-ltree validator, as it does not accept numbers for the first label char
# (the PostgreSQL extension seems to allow it)
# TODO: PR on django-ltree?
overridden_path_validator = RegexValidator(
    r"^(?P<root>[a-zA-Z0-9_]*)(?:.[a-zA-Z0-9_]+)*$",
    "A label is a sequence of alphanumeric characters and underscores separated by dots.",
    "invalid",
)


class PathFormField(BasePathFormField):
    default_validators = []


class PathField(BasePathField):
    default_validators = []

    def formfield(self, **kwargs):
        kwargs["form_class"] = PathFormField
        kwargs["widget"] = TextInput(attrs={"class": "vTextField"})

        return super(BasePathField, self).formfield(
            **kwargs
        )  # call super() on grandparent
