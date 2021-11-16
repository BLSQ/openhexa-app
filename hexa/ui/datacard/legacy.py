from __future__ import annotations

import typing

from django import forms
from django.contrib import messages
from django.template import loader
from django.utils.translation import ugettext_lazy as _

import hexa.ui.datacard.actions
from hexa.ui.datacard.base import BaseMeta
from hexa.ui.datacard.properties import Property
from hexa.ui.utils import StaticText, get_item_value

from .base import DatacardComponent


class LegacyDatacardOptions:
    """Container for datacard meta (config)"""

    def __init__(
        self,
        *,
        title: typing.Union[StaticText, str],
        subtitle: typing.Union[StaticText, str],
        sections: typing.Sequence[Section],
        image_src: str = None,
        actions: list[hexa.ui.datacard.actions.Action] = None
    ):
        self.sections = sections
        self.title = title
        self.subtitle = subtitle
        self.image_src = image_src
        self.actions = actions


class LegacyDatacardMeta(BaseMeta):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, LegacyDatacardMeta)]
        if not parents:
            return new_class

        new_class._meta = LegacyDatacardOptions(
            sections=mcs.find(attrs, Section),
            title=attrs.get("title"),
            subtitle=attrs.get("subtitle"),
            image_src=attrs.get("image_src"),
            actions=attrs.get("actions", []),
        )

        return new_class


class LegacyDatacard(metaclass=LegacyDatacardMeta):
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
            "actions": self._actions,
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

    def bind(self, datacard: LegacyDatacard):
        return BoundSection(self, datacard=datacard)

    @property
    def properties(self):
        return self._meta.properties.values()

    @property
    def template(self):
        return "ui/datacard/section.html"


class BoundSection:
    def __init__(self, unbound_section: Section, *, datacard: LegacyDatacard) -> None:
        self.unbound_section = unbound_section
        self.datacard = datacard
        self.form = self.build_form()
        self.properties = [p.bind(self) for p in self.unbound_section.properties]

    def build_form(self):
        editable_properties = [p for p in self.unbound_section.properties if p.editable]

        if len(editable_properties) == 0:
            return None

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
        template = loader.get_template("ui/datacard/section.html")

        context = {
            "name": self.unbound_section.name,
            "title": _(self.unbound_section.title)
            if self.unbound_section.title is not None
            else None,
            "properties": self.properties,
            "editable": any(p.editable for p in self.properties),
        }

        return template.render(context, request=self.datacard.request)
