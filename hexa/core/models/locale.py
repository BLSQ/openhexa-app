from collections import OrderedDict
from functools import lru_cache

from django.conf import locale
from django.db import models

from hexa.core.models.choices import DynamicTextChoices


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
    """Custom choice field using Django locales."""

    description = "A locale string (as specified in django.conf.locale.LANG_INFO)"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 7  # Some exceptions to the 5 chars limit in LANG_INFO
        kwargs["choices"] = Locale.choices
        super().__init__(*args, **kwargs)
