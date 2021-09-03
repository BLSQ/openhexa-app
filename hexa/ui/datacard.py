from django.forms import Form
from django.template import loader
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from markdown import markdown as to_markdown

from hexa.core.date_utils import date_format as do_date_format
from hexa.core.models.locale import Locale
from hexa.ui.utils import get_item_value


class DatacardOptions:
    """Container for datacard meta (config)"""

    def __init__(self, *, title, subtitle, sections, image_src=None, actions=None):
        self.sections = sections
        self.title = title
        self.subtitle = subtitle
        self.image_src = image_src
        self.actions = actions
        # TODO: fields ?


class SectionOptions:
    """Container for section meta (config)"""

    def __init__(self, *, properties, fields):
        self.properties = properties
        self.fields = fields


class BaseMeta(type):
    """Metaclass for properties registration"""

    @staticmethod
    def find(attrs, new_class, of_type):
        elected = {}
        for name, unbound in [
            (k, v) for k, v in attrs.items() if isinstance(v, of_type)
        ]:
            elected[name] = unbound.bind(name, new_class)

        return elected


class DatacardMeta(BaseMeta):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, DatacardMeta)]
        if not parents:
            return new_class

        new_class._meta = DatacardOptions(
            sections=mcs.find(attrs, new_class, Section),
            title=attrs["title"],
            subtitle=attrs["subtitle"],
            image_src=attrs["image_src"],
            actions=[action.bind(new_class) for action in attrs.get("actions", [])],
        )

        return new_class


class Datacard(metaclass=DatacardMeta):
    title = None
    subtitle = None
    image_src = None

    def __init__(self, model, *, request):
        self.model = model
        self.request = request

    def __str__(self):
        """Render the datacard"""

        template = loader.get_template("ui/datacard/datacard.html")

        action_data = []
        for action_instance in self._meta.actions:
            action_data.append(
                {
                    "template": action_instance.template,
                    **action_instance.context(self.model),
                }
            )

        section_data = []
        for section_name, section_instance in self._meta.sections.items():
            section_data.append(
                {
                    "template": section_instance.template,
                    **section_instance.context(self.model),
                }
            )

        context = {
            "sections": section_data,
            "actions": action_data,
            "title": get_item_value(
                self.model, self._meta.title, container=self, exclude=PropertyLike
            ),
            "subtitle": get_item_value(
                self.model, self._meta.subtitle, container=self, exclude=PropertyLike
            ),
            "image_src": get_item_value(
                self.model, self._meta.image_src, container=self, exclude=PropertyLike
            ),
        }

        return template.render(context, request=self.request)


class SectionMeta(BaseMeta):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, SectionMeta)]
        if not parents:
            return new_class

        properties = mcs.find(attrs, new_class, Property)
        new_class._meta = SectionOptions(
            properties=properties,
            fields={k: v for k, v in properties.items() if v.editable},
        )

        return new_class


class PropertyLike:
    def __init__(self, *, label=None, editable=False):
        self._label = label
        self.name = None
        self.card = None
        self.editable = editable

    def bind(self, name, card):
        self.name = name
        self.card = card

        return self

    @property
    def label(self):
        return _(self._label) if self._label is not None else _(self.name.capitalize())

    @property
    def template(self):
        raise NotImplementedError(
            "Each Property-like class should implement the template() property"
        )

    def data(self, item):
        raise NotImplementedError(
            "Each Property-like class should implement the data() method"
        )

    def get_value(self, item, accessor):
        if self.card is None:
            raise ValueError("Cannot get item value for unbound property")

        return get_item_value(item, accessor, container=self.card, exclude=PropertyLike)


class Property(PropertyLike):
    """Base property class (to be extended)"""

    @property
    def template(self):
        raise NotImplementedError(
            "Each Property class should implement the template() property"
        )

    @property
    def input_template(self):
        return None
        raise NotImplementedError(
            "Each Property class should implement the input_template() property"
        )

    def data(self, item):
        raise NotImplementedError(
            "Each Property class should implement the data() method"
        )


class Section(PropertyLike, metaclass=SectionMeta):
    title = None

    def build_form(self):
        form = Form()
        for property_name, property_instance in self._meta.properties.items():
            if property_instance.editable:
                form.fields[property_name] = property_instance.build_field()

        return form

    def context(self, item):
        property_data = []
        for property_name, property_instance in self._meta.properties.items():
            property_data.append(
                {
                    "template": property_instance.template,
                    "input_template": property_instance.input_template,
                    "data": property_instance.data(item),
                    "label": property_instance.label,
                    "editable": property_instance.editable,
                }
            )
        return {
            "title": _(self.title) if self.title is not None else None,
            "properties": property_data,
        }

    @property
    def template(self):
        return "ui/datacard/section.html"


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

    def data(self, item):
        text_value = self.get_value(item, self.text)

        return {
            "text": mark_safe(to_markdown(text_value)) if self.markdown else text_value,
            "markdown": self.markdown,
        }


class CodeProperty(Property):
    def __init__(self, *, code, language, **kwargs):
        super().__init__(**kwargs)
        self.code = code
        self.language = language

    @property
    def template(self):
        return "ui/datacard/property_code.html"

    def data(self, item):

        return {"code": self.get_value(item, self.code), "language": self.language}


class BooleanProperty(Property):
    def __init__(self, *, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value

    @property
    def template(self):
        return "ui/datacard/property_boolean.html"

    def data(self, item):
        value = self.get_value(item, self.value)

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

    def data(self, item):
        locale_value = self.get_value(item, self.locale)

        return {"text": Locale[locale_value].label}


class CountryProperty(Property):
    def __init__(self, *, countries=None, **kwargs):
        super().__init__(**kwargs)

        self.countries = countries

    @property
    def template(self):
        return "ui/datacard/property_country.html"

    def data(self, item):
        return {"countries": self.get_value(item, self.countries)}


class TagProperty(Property):
    def __init__(self, *, tags=None, **kwargs):
        super().__init__(**kwargs)

        if tags is None:  # TODO: Replace by name guessing
            tags = "tags.all"

        self.tags = tags

    @property
    def template(self):
        return "ui/datacard/property_tag.html"

    def data(self, item):
        tags_value = self.get_value(item, self.tags)

        return {
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

    def data(self, item):
        url_value = self.get_value(item, self.url)
        text_value = (
            self.get_value(item, self.text) if self.text is not None else url_value
        )

        return {"text": text_value, "url": url_value}


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

    def data(self, item):
        return {
            "date": self.format_date(self.get_value(item, self.date)),
        }


class Action:
    def __init__(self, label, url, icon=None, method="post"):
        self.label = label
        self.icon = icon
        self.url = url
        self.method = method
        self.card = None

    def bind(self, card: Datacard):
        self.card = card

        return self

    def get_value(self, item, accessor):
        if self.card is None:
            raise ValueError("Cannot get item value for unbound action")

        return get_item_value(item, accessor, container=self.card, exclude=Action)

    @property
    def template(self):
        return "ui/datacard/action.html"

    def context(self, item):
        return {
            "url": self.get_value(item, self.url),
            "label": _(self.label),
            "icon": self.icon,
            "method": self.method,
        }
