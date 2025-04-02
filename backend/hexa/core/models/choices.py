from django.db import models
from django.db.models.enums import ChoicesMeta


class DynamicChoicesMeta(ChoicesMeta):
    """A metaclass for creating dynamic enum choices."""

    def __new__(metacls, classname, bases, classdict):
        # We don't want to process anything in the base DynamicTextChoices class - only in its subclasses
        if classname != "DynamicTextChoices":
            try:
                build_function = classdict["build_choices"].__get__(0)
            except (KeyError, AttributeError):
                raise NotImplementedError(
                    "You need to provide a build_choices() method when using the DynamicChoicesMeta metaclass"
                )

            choices_data = build_function()
            if not isinstance(choices_data, dict):
                raise ValueError("build_choices() should return a dict")

            for name, choice_data in choices_data.items():
                classdict[name] = choice_data

        return super().__new__(metacls, classname, bases, classdict)


class DynamicTextChoices(models.TextChoices, metaclass=DynamicChoicesMeta):
    @staticmethod
    def build_choices():
        raise NotImplementedError(
            "DynamicTextChoices subclasses must provide a static build_choices() method"
        )
