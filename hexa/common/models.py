from collections import OrderedDict
from functools import lru_cache
import uuid

from django.conf import locale
from django.db import models
from django.db.models.enums import ChoicesMeta


class Base(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)


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


class Locale(DynamicTextChoices):
    @staticmethod
    @lru_cache
    def build_choices():
        """Build the locale choices from LANG_INFO, excluding the ones with no name"""

        filtered_lang_info = {
            code: info for code, info in locale.LANG_INFO.items() if "name" in info
        }
        sorted_codes = sorted(
            filtered_lang_info.keys(), key=lambda c: filtered_lang_info[c]["name"]
        )

        return OrderedDict(
            {
                lang_code: (lang_code, filtered_lang_info[lang_code]["name"])
                for lang_code in sorted_codes
            }
        )


class LocaleField(models.CharField):
    description = "A locale string (as specified in django.conf.locale.LANG_INFO)"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 7  # Some exceptions to the 5 chars limit in LANG_INFO
        kwargs["choices"] = Locale.choices
        super().__init__(*args, **kwargs)


class PostgresTextSearchConfigField(models.CharField):
    description = "A Postgres text search config value (see pg_ts_config)"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 100
        # TODO: more choices
        kwargs["choices"] = [
            ("simple", "simple"),
            ("french", "french"),
            ("english", "english"),
        ]
        kwargs["default"] = "simple"
        super().__init__(*args, **kwargs)
