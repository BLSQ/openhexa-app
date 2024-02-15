from __future__ import annotations

import typing

from django import forms
from django.contrib import messages
from django.http import HttpRequest
from django.template import loader
from django.utils.translation import gettext_lazy as _

import hexa.ui.datacard.actions
from hexa.ui.datacard.base import BaseMeta
from hexa.ui.datacard.properties import Property
from hexa.ui.datagrid import DjangoModel
from hexa.ui.utils import StaticText, get_item_value

from .base import DatacardComponent


class DatacardOptions:
    """Container for datacard meta (config)"""

    def __init__(
        self,
        *,
        title: typing.Union[StaticText, str],
        subtitle: typing.Union[StaticText, str],
        sections: typing.Sequence[Section],
        image_src: str = None,
        actions: list[hexa.ui.datacard.actions.Action] = None,
    ):
        self.sections = sections
        self.title = title
        self.subtitle = subtitle
        self.image_src = image_src
        self.actions = actions


class DatacardMeta(BaseMeta):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, DatacardMeta)]
        if not parents:
            return new_class

        new_class._meta = DatacardOptions(
            sections=mcs.find(attrs, Section),
            title=attrs.get("title"),
            subtitle=attrs.get("subtitle"),
            image_src=attrs.get("image_src"),
            actions=attrs.get("actions", []),
        )

        return new_class


class Datacard(metaclass=DatacardMeta):
    title = None
    subtitle = None
    image_src = None

    def __init__(self, model, *, request):
        self.model = model
        self.request = request

        self._sections = {k: v.bind(self) for k, v in self._meta.sections.items()}
        self._actions = [a.bind(self) for a in self._meta.actions]

    def save(self):
        section_name = self.request.POST["section_name"]
        self._sections[section_name].save()

        return True

    def __str__(self):
        """Render the datacard"""
        template = loader.get_template("ui/datacard/datacard.html")

        context = {
            "sections": self._sections.values(),
            "actions": [a for a in self._actions if a.is_enabled(self.request)],
            "title": get_item_value(
                self.model,
                self._meta.title,
                container=self,
                exclude=DatacardComponent,
            )
            if self._meta.title
            else None,
            "subtitle": get_item_value(
                self.model,
                self._meta.subtitle,
                container=self,
                exclude=DatacardComponent,
            )
            if self._meta.subtitle
            else None,
            "image_src": get_item_value(
                self.model,
                self._meta.image_src,
                container=self,
                exclude=DatacardComponent,
            )
            if self._meta.image_src
            else None,
        }

        return template.render(context, request=self.request)


class SectionOptions:
    """Container for section meta (config)"""

    def __init__(self, *, properties):
        self.properties = properties


class SectionMeta(BaseMeta):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, SectionMeta)]
        if not parents:
            return new_class

        properties = mcs.find(attrs, Property)
        new_class._meta = SectionOptions(
            properties=properties,
        )

        return new_class


class Section(DatacardComponent, metaclass=SectionMeta):
    title = None

    def __init__(self, value=None):
        self.name = None
        self.value = value
        self.datacard = None

    def bind(self, datacard: Datacard):
        return BoundSection(self, datacard=datacard)

    @property
    def properties(self):
        return self._meta.properties.values()

    @property
    def template(self):
        return "ui/datacard/section.html"

    @property
    def is_editable(self):
        return any([p for p in self.properties if p.editable])

    def context(
        self, model: DjangoModel, card: Datacard
    ) -> typing.Mapping[str, typing.Any]:
        return {}

    def is_enabled(self, request: HttpRequest, model):
        return True


class BoundSection:
    def __init__(self, unbound_section: Section, *, datacard: Datacard) -> None:
        self.unbound_section = unbound_section
        self.datacard = datacard
        self.form = self.build_form()
        self.properties = [p.bind(self) for p in self.unbound_section.properties]

    def is_enabled(self, request: HttpRequest, model):
        return self.unbound_section.is_enabled(request, model)

    def build_form(self):
        if not self.unbound_section.is_editable:
            return None

        editable_properties = [p for p in self.unbound_section.properties if p.editable]

        if not hasattr(self.unbound_section, "Meta"):
            raise ValueError("Need a Meta for forms")

        class SectionForm(forms.ModelForm):
            class Meta:
                model = self.unbound_section.Meta.model
                fields = [p.name for p in editable_properties]
                widgets = {
                    p.name: p.input_widget
                    for p in editable_properties
                    if p.input_widget is not None
                }

        return SectionForm(
            instance=self.model,
            data=self.request.POST if self.request.method == "POST" else None,
        )

    def save(self):
        self.form.save()
        messages.success(self.request, _("Save successful!"))

    @property
    def model(self):
        return (
            self.datacard.model
            if self.unbound_section.value is None
            else get_item_value(self.datacard.model, self.unbound_section.value)
        )

    @property
    def request(self):
        return self.datacard.request

    def __str__(self):
        if self.is_enabled(self.datacard.request, self.model):
            template = loader.get_template(self.unbound_section.template)

            context = {
                "name": self.unbound_section.name,
                "title": _(self.unbound_section.title)
                if self.unbound_section.title is not None
                else None,
                "properties": self.properties,
                "editable": self.unbound_section.is_editable,
                **self.unbound_section.context(self.model, self.datacard),
            }

            return template.render(context, request=self.datacard.request)
        else:
            return ""
