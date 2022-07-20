from __future__ import annotations

import typing
import urllib.parse

from django import forms
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _
from markdown import markdown as to_markdown

import hexa.ui.datacard
from hexa.core.date_utils import date_format as do_date_format
from hexa.core.models.behaviors import Status
from hexa.core.models.locale import Locale
from hexa.ui.utils import StaticText, get_item_value

from .base import DatacardComponent


class Property(DatacardComponent):
    """Base property class (to be extended)"""

    def __init__(self, *, label=None, editable=False):
        self._label = label
        self.name = None
        self.editable = editable

    @property
    def template(self):
        raise NotImplementedError(
            "Each Property class should implement the template() property"
        )

    @property
    def input_template(self):
        return "ui/datacard/input_property.html"

    @property
    def input_widget(self):
        return None

    def base_context(self, model, section, is_edit=False):
        return {
            "property_label": _(self._label)
            if self._label is not None
            else _(self.name.capitalize()),
        }

    def context(self, model, section, is_edit=False):
        raise NotImplementedError(
            "Each Property class should implement the context() method"
        )

    def bind(self, section: hexa.ui.datacard.Section):
        return BoundProperty(self, section=section)

    @staticmethod
    def get_value(model, accessor, container=None):
        return get_item_value(
            model, accessor, container=container, exclude=DatacardComponent
        )


class BoundProperty:
    def __init__(self, unbound_property, *, section) -> None:
        self.unbound_property = unbound_property
        self.section = section

    @property
    def editable(self):
        return self.unbound_property.editable

    @property
    def name(self):
        return self.unbound_property.name

    def __str__(self):
        template = loader.get_template(self.unbound_property.template)

        return template.render(
            {
                **self.unbound_property.base_context(
                    self.section.model, self.section.unbound_section
                ),
                **self.unbound_property.context(
                    self.section.model, self.section.unbound_section
                ),
            },
            request=self.section.request,
        )

    def as_field(self):
        template = loader.get_template(self.unbound_property.input_template)

        return template.render(
            {
                "field": self.section.form[self.name],
                **self.unbound_property.base_context(
                    self.section.model, self.section.unbound_section, is_edit=True
                ),
                **self.unbound_property.context(
                    self.section.model, self.section.unbound_section, is_edit=True
                ),
            },
            request=self.section.request,
        )


class TextProperty(Property):
    def __init__(self, *, text, translate=True, markdown=False, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.markdown = markdown
        self.translate = translate

    @property
    def template(self):
        return "ui/datacard/property_text.html"

    def context(self, model, section, **kwargs):
        text_value = self.get_value(model, self.text, container=section)

        return {
            "text": mark_safe(to_markdown(text_value)) if self.markdown else text_value,
            "markdown": self.markdown,
            "translate": self.translate,
        }

    def build_field(self):
        return forms.CharField(
            widget=forms.TextInput if not self.markdown else forms.Textarea
        )

    @property
    def input_widget(self):
        if self.markdown:
            return forms.Textarea(
                attrs={
                    "class": "form-input shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                }
            )

        return forms.TextInput(
            attrs={
                "class": "form-input shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
            }
        )


class CodeProperty(Property):
    def __init__(self, *, code, language, **kwargs):
        super().__init__(**kwargs)
        self.code = code
        self.language = language

    @property
    def template(self):
        return "ui/datacard/property_code.html"

    def context(self, model, section, **kwargs):
        return {
            "code": self.get_value(model, self.code, container=section),
            "language": self.language,
        }


class BooleanProperty(Property):
    def __init__(self, *, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    @property
    def template(self):
        return "ui/datacard/property_boolean.html"

    def context(self, model, section, **kwargs):
        value = self.get_value(model, self.value, container=section)

        return {
            "text": _("Yes") if value is True else _("No"),
        }


class LocaleProperty(Property):
    def __init__(self, *, locale, **kwargs):
        super().__init__(**kwargs)
        self.locale = locale

    @property
    def template(self):
        return "ui/datacard/property_text.html"

    def context(self, model, section, **kwargs):
        locale_value = self.get_value(model, self.locale, container=section)

        return {"text": Locale[locale_value].label}


class TagProperty(Property):
    def __init__(self, *, value=None, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    @property
    def template(self):
        return "ui/datacard/property_tag.html"

    def context(self, model, section, is_edit=False):
        return {
            "tags": [
                {"label": t.name}
                for t in self.get_value(model, self.value, container=section)
            ],
        }

    @property
    def input_widget(self):
        return forms.SelectMultiple(
            attrs={
                # "class": "form-input block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md",
                "x-data": "TomSelectable()",
                "x-init": "init($el)",
            }
        )


class CountryProperty(TagProperty):
    def context(self, model, section, **kwargs):
        return {
            "tags": [
                {"label": c.name, "image": c.flag}
                for c in self.get_value(model, self.value, container=section)
            ],
        }


class URLProperty(Property):
    def __init__(
        self,
        *,
        url: str,
        text: typing.Union[str, StaticText] = None,
        external: bool = True,
        track=True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.text = text
        self.url = url
        self.external = external
        self.track = track

    @property
    def template(self):
        return "ui/datacard/property_url.html"

    def context(self, model, section, **kwargs):
        url_value = self.get_value(model, self.url, container=section)
        text_value = (
            self.get_value(model, self.text, container=section)
            if self.text is not None
            else url_value
        )

        if self.track and url_value is not None and url_value.startswith("http"):
            # external url -> track it
            url_value = (
                reverse("metrics:save_redirect")
                + "?to="
                + urllib.parse.quote(url_value, safe="")
            )

        return {"text": text_value, "url": url_value, "external": self.external}


class OwnerProperty(URLProperty):
    @property
    def input_widget(self):
        return forms.Select(
            attrs={
                "class": "form-input block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            }
        )


class UserProperty(Property):
    def __init__(self, *, user: str, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    def context(self, model, section, **kwargs):
        return {"user": self.get_value(model, self.user, section)}

    @property
    def template(self):
        return "ui/datacard/property_user.html"

    @property
    def input_widget(self):
        return forms.Select(
            attrs={
                "class": "form-input block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            }
        )


class DateProperty(Property):
    def __init__(self, *, date=None, date_format="M d, H:i:s (e)", **kwargs):
        super().__init__(**kwargs)

        self.date = date
        self.date_format = date_format

    @property
    def template(self):
        return "ui/datacard/property_date.html"

    def format_date(self, date):  # TODO: duplicated from datagrid -> move somewhere
        if date is None:
            return date

        if self.date_format == "timesince":
            if (timezone.now() - date).seconds < 60:
                return _("Just now")

            return f"{timesince(date)} {_('ago')}"
        else:
            return do_date_format(date, self.date_format)

    def context(self, model, section, **kwargs):
        return {
            "date": self.format_date(
                self.get_value(model, self.date, container=section)
            ),
        }


class StatusProperty(Property):
    COLOR_MAPPINGS = {
        Status.SUCCESS: "green",
        Status.ERROR: "red",
        Status.RUNNING: "yellow",
        Status.PENDING: "gray",
        Status.UNKNOWN: "gray",
    }

    LABEL_MAPPINGS = {
        Status.SUCCESS: _("Success"),
        Status.ERROR: _("Error"),
        Status.RUNNING: _("Running"),
        Status.PENDING: _("Pending"),
        Status.UNKNOWN: _("Unknown"),
    }

    def __init__(self, *, value=None, **kwargs):
        super().__init__(**kwargs)

        self.value = value

    @property
    def template(self):
        return "ui/datacard/property_status.html"

    def context(self, model, section, **kwargs):
        status = self.get_value(model, self.value, container=section)

        return {
            "color": self.COLOR_MAPPINGS.get(status),
            "label": self.LABEL_MAPPINGS.get(status),
        }
