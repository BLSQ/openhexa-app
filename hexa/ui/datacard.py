from django import forms
from django.template import loader
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from markdown import markdown as to_markdown

from hexa.core.date_utils import date_format as do_date_format
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
        self.actions = actions
        self.bound = False

    def bind_children(self, datacard: "Datacard"):
        self.sections = {k: v.bind(datacard) for k, v in self.sections.items()}
        self.actions = [a.bind(datacard) for a in self.actions]
        self.bound = True


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
        self._meta.bind_children(self)

    def save(self):
        section_name = self.request.POST["section_name"]
        self._meta.sections[section_name].save()

    def __str__(self):
        """Render the datacard"""

        template = loader.get_template("ui/datacard/datacard.html")

        context = {
            "sections": self._meta.sections.values(),
            "actions": self._meta.actions,
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

    def __init__(self, *, properties, fields):
        self.properties = properties
        self.bound = False

    def bind_children(self, section: "Section"):
        self.properties = {k: v.bind(section) for k, v in self.properties.items()}
        self.bound = True


class SectionMeta(BaseMeta):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, SectionMeta)]
        if not parents:
            return new_class

        properties = mcs.find(attrs, Property)
        new_class._meta = SectionOptions(
            properties=properties,
            fields={k: v for k, v in properties.items() if v.editable},
        )

        return new_class


class Section(metaclass=SectionMeta):
    title = None

    def __init__(self, value=None):
        self.name = None
        self.value = value
        self.datacard = None

    def bind(self, datacard: Datacard):
        self._meta.bind_children(self)
        self.datacard = datacard

    @property
    def form(self):
        editable_properties = [p for p in self._meta.properties if p.editable]

        if len(editable_properties) == 0:
            return None

        if not hasattr(self, "Meta"):
            raise ValueError("Need a Meta for forms")

        class SectionForm(forms.ModelForm):
            class Meta:
                model = self.Meta.model
                fields = [p.name for p in editable_properties]

        return SectionForm(
            instance=self.model,
            data=self.request.POST if self.request.method == "POST" else None,
        )

    def save(self):
        if self.form.is_valid():
            self.save()

    def __str__(self):
        """Render the section"""

        template = loader.get_template("ui/datacard/section.html")
        properties = self._meta.properties.values()

        context = {
            "name": self.name,
            "title": _(self.title) if self.title is not None else None,
            "properties": properties,
            "editable": any(p.editable for p in properties),
        }

        return template.render(context, request=self.datacard.request)

    @property
    def template(self):
        return "ui/datacard/section.html"


class Property:
    """Base property class (to be extended)"""

    def __init__(self, *, label=None, editable=False, hidden=False, **kwargs):
        self._label = label
        self.name = None
        self.editable = editable
        self.hidden = hidden
        self.section = None

    @property
    def template(self):
        raise NotImplementedError(
            "Each Property class should implement the template() property"
        )

    @property
    def input_template(self):
        raise NotImplementedError(
            "Each Property class should implement the template() property"
        )

    def context(self, model, is_edit=False):
        context = {"label": self.label}
        if is_edit:
            context["field"] = self.section.form[self.name]

        return context

    @property
    def label(self):
        return _(self._label) if self._label is not None else _(self.name.capitalize())

    def bind(self, section: "Section"):
        self.section = section

    def get_value(self, model, accessor):
        if self.section is None:
            raise ValueError("Cannot get item value for unbound property")

        return get_item_value(
            model, accessor, container=self.section, exclude=(Section, Property)
        )

    def __str__(self):
        """Render the property"""

        if self.hidden:
            return ""

        template = loader.get_template(self.template)

        return template.render(
            self.context(self.section.model), request=self.section.request
        )

    def as_field(self):
        template = loader.get_template(self.input_template)

        return template.render(
            self.context(self.section.model, is_edit=True), request=self.section.request
        )


class TextProperty(Property):
    def __init__(self, *, text, markdown=False, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.markdown = markdown

    @property
    def template(self):
        return "ui/datacard/property_text.html"

    @property
    def input_template(self):
        return "ui/datacard/input_property_text.html"

    def context(self, model, **kwargs):
        text_value = self.get_value(model, self.text)

        return {
            **super().context(model, **kwargs),
            "text": mark_safe(to_markdown(text_value)) if self.markdown else text_value,
            "markdown": self.markdown,
        }

    def get_field_value(self, model):
        return self.get_value(model, self.text)

    def build_field(self):
        return forms.CharField(
            widget=forms.TextInput if not self.markdown else forms.Textarea
        )


class CodeProperty(Property):
    def __init__(self, *, code, language, **kwargs):
        super().__init__(**kwargs)
        self.code = code
        self.language = language

    @property
    def template(self):
        return "ui/datacard/property_code.html"

    def context(self, model, **kwargs):
        return {
            **super().context(model, **kwargs),
            "code": self.get_value(model, self.code),
            "language": self.language,
        }


class BooleanProperty(Property):
    def __init__(self, *, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    @property
    def template(self):
        return "ui/datacard/property_boolean.html"

    def context(self, model, **kwargs):
        value = self.get_value(model, self.value)

        return {
            **super().context(**kwargs),
            "text": _("Yes") if value is True else _("No"),
        }


class LocaleProperty(Property):
    def __init__(self, *, locale, **kwargs):
        super().__init__(**kwargs)
        self.locale = locale

    @property
    def template(self):
        return "ui/datacard/property_text.html"

    def context(self, model, **kwargs):
        locale_value = self.get_value(model, self.locale)

        return {**super().context(model, **kwargs), "text": Locale[locale_value].label}


class CountryProperty(Property):
    def __init__(self, *, countries=None, **kwargs):
        super().__init__(**kwargs)

        self.countries = countries

    @property
    def template(self):
        return "ui/datacard/property_country.html"

    def context(self, model, **kwargs):
        return {
            **super().context(model, **kwargs),
            "countries": self.get_value(model, self.countries),
        }


class TagProperty(Property):
    def __init__(self, *, tags=None, **kwargs):
        super().__init__(**kwargs)

        if tags is None:  # TODO: Replace by name guessing
            tags = "tags.all"

        self.tags = tags

    @property
    def template(self):
        return "ui/datacard/property_tag.html"

    def context(self, model, **kwargs):
        tags_value = self.get_value(model, self.tags)

        return {
            **super().context(model, **kwargs),
            "tags": tags_value,
        }


class URLProperty(Property):
    def __init__(self, *, url, text=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.url = url

    @property
    def template(self):
        return "ui/datacard/property_url.html"

    def context(self, model, **kwargs):
        url_value = self.get_value(model, self.url)
        text_value = (
            self.get_value(model, self.text) if self.text is not None else url_value
        )

        return {
            **super().context(model, **kwargs),
            "text": text_value,
            "url": url_value,
        }


class HiddenProperty(Property):
    def __init__(self, *, value, **kwargs):
        super().__init__(editable=True, hidden=True, **kwargs)
        self.value = value

    @property
    def template(self):
        return None

    @property
    def input_template(self):
        return "ui/datacard/input_property_hidden.html"

    def context(self, model, **kwargs):
        return {
            **super().context(model, **kwargs),
            "value": self.get_value(model, self.value),
        }

    def get_field_value(self, model):
        return self.get_value(model, self.value)

    def build_field(self):
        return forms.CharField(widget=forms.HiddenInput)


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

    def context(self, model, **kwargs):
        return {
            **super().context(model, **kwargs),
            "date": self.format_date(self.get_value(model, self.date)),
        }


class Action:
    def __init__(self, label, url, icon=None, method="post"):
        self.label = label
        self.icon = icon
        self.url = url
        self.method = method
        self.datacard = None

    def bind(self, datacard: Datacard):
        self.datacard = datacard

    def get_value(self, model, accessor):
        if self.datacard is None:
            raise ValueError("Cannot get model value for unbound action")

        return get_item_value(model, accessor, container=self.datacard, exclude=Action)

    @property
    def template(self):
        return "ui/datacard/action.html"

    def __str__(self):
        template = loader.get_template(self.template)

        context = {
            "url": self.get_value(self.datacard.model, self.url),
            "label": _(self.label),
            "icon": self.icon,
            "method": self.method,
        }

        return template.render(context, request=self.datacard.request)
