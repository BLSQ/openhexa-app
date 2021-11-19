import urllib.parse

from django import forms
from django.contrib import messages
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from markdown import markdown as to_markdown

from hexa.core.date_utils import date_format as do_date_format
from hexa.core.models import WithStatus
from hexa.core.models.locale import Locale
from hexa.ui.utils import get_item_value


class BaseMeta(type):
    """Metaclass for properties registration"""

    @staticmethod
    def find(attrs, of_type):
        elected = {}
        for name, instance in [
            (k, v) for k, v in attrs.items() if isinstance(v, of_type)
        ]:
            instance.name = name
            elected[name] = instance

        return elected


class DatacardOptions:
    """Container for datacard meta (config)"""

    def __init__(self, *, title, subtitle, sections, image_src=None, actions=None):
        self.sections = sections
        self.title = title
        self.subtitle = subtitle
        self.image_src = image_src
        self.actions: list[Action] = actions


class DatacardMeta(BaseMeta):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, DatacardMeta)]
        if not parents:
            return new_class

        new_class._meta = DatacardOptions(
            sections=mcs.find(attrs, Section),
            title=attrs["title"],
            subtitle=attrs["subtitle"],
            image_src=attrs["image_src"],
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
            "actions": self._actions,
            "title": get_item_value(
                self.model,
                self._meta.title,
                container=self,
                exclude=(Property, Section),
            ),
            "subtitle": get_item_value(
                self.model,
                self._meta.subtitle,
                container=self,
                exclude=(Property, Section),
            ),
            "image_src": get_item_value(
                self.model,
                self._meta.image_src,
                container=self,
                exclude=(Property, Section),
            ),
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


class Section(metaclass=SectionMeta):
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


class BoundSection:
    def __init__(self, unbound_section: Section, *, datacard: Datacard) -> None:
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


class Property:
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

    def bind(self, section: "Section"):
        return BoundProperty(self, section=section)

    @staticmethod
    def get_value(model, accessor, container=None):
        return get_item_value(
            model, accessor, container=container, exclude=(Section, Property)
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
    def __init__(self, *, url, text=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.url = url

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

        if url_value and url_value.startswith("http"):
            # external url -> track it
            url_value = (
                reverse("metrics:save_redirect")
                + "?to="
                + urllib.parse.quote(url_value, safe="")
            )

        return {
            "text": text_value,
            "url": url_value,
        }


class OwnerProperty(URLProperty):
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
        WithStatus.SUCCESS: "green",
        WithStatus.ERROR: "red",
        WithStatus.RUNNING: "yellow",
        WithStatus.PENDING: "gray",
        WithStatus.UNKNOWN: "gray",
    }

    LABEL_MAPPINGS = {
        WithStatus.SUCCESS: _("Success"),
        WithStatus.ERROR: _("Error"),
        WithStatus.RUNNING: _("Running"),
        WithStatus.PENDING: _("Pending"),
        WithStatus.UNKNOWN: _("Unknown"),
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


class Action:
    def __init__(self, label, url, icon=None, method="post"):
        self.label = label
        self.icon = icon
        self.url = url
        self.method = method

    def bind(self, datacard: Datacard):
        return BoundAction(self, datacard=datacard)

    def get_value(self, model, accessor, container=None):
        return get_item_value(model, accessor, container=container, exclude=Action)

    @property
    def template(self):
        return "ui/datacard/action.html"

    def context(self, model, card: Datacard):
        return {
            "url": self.get_value(model, self.url, container=card),
            "label": _(self.label),
            "icon": self.icon,
            "method": self.method,
        }


class BoundAction:
    def __init__(self, unbound_action: Action, *, datacard: Datacard):
        self.unbound_action = unbound_action
        self.datacard = datacard

    def __str__(self):
        template = loader.get_template(self.unbound_action.template)

        return template.render(
            self.unbound_action.context(self.datacard.model, self.datacard),
            request=self.datacard.request,
        )
