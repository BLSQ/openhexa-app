from django.core.paginator import Paginator
from django.template import loader
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _


class DatagridOptions:
    """Container for datagrid meta (config)"""

    def __init__(self, *, columns):
        self.columns = columns


class DatagridMeta(type):
    """Metaclass for column registration"""

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, DatagridMeta)]
        if not parents:
            return new_class

        columns = {}
        for column_name, unbound_column in [
            (k, v) for k, v in attrs.items() if isinstance(v, Column)
        ]:
            columns[column_name] = unbound_column.bind(column_name, new_class)
        new_class._meta = DatagridOptions(columns=columns)

        return new_class


class Datagrid(metaclass=DatagridMeta):
    def __init__(self, queryset, *, paginate=True, per_page=20, page=1, more_url=None):
        self.paginator = Paginator(queryset, per_page)
        self.page = self.paginator.page(page)
        self.paginate = paginate
        self.more_url = more_url

    def __str__(self):
        """Render the datagrid"""

        template = loader.get_template("ui/datagrid/datagrid.html")
        row_data = []
        for row in self.page:
            single_row_data = []
            for column_name, column in self._meta.columns.items():
                single_row_data.append(
                    {"template": column.template, "data": column.data(row)}
                )

            row_data.append(single_row_data)

        context = {
            "rows": row_data,
            "columns": self._meta.columns.values(),
            "pagination": {
                "display": self.paginate,
                "item_label": _("Item") if self.paginator.count == 1 else _("items"),
                "previous_page_number": self.page.previous_page_number()
                if self.page.has_previous()
                else None,
                "next_page_number": self.page.next_page_number()
                if self.page.has_next()
                else None,
                "current_page_number": self.page.number,
                "current_page_count": len(self.page),
                "total_count": self.total_count,
                "total_page_count": self.total_page_count,
                "range": self.paginator.get_elided_page_range(
                    self.page.number, on_ends=1
                ),
                "start_index": self.start_index,
                "end_index": self.end_index,
            },
            "more_url": self.more_url,
        }

        return template.render(context)

    @property
    def total_count(self):
        return self.paginator.count

    @property
    def total_page_count(self):
        return self.paginator.num_pages

    @property
    def start_index(self):
        return self.page.start_index()

    @property
    def end_index(self):
        return self.page.end_index()


class Column:
    """Base column class (to be extended)"""

    def __init__(self, *, label=None, hide_label=False):
        self._label = label
        self.hide_label = hide_label
        self.name = None
        self.grid = None

    def bind(self, name, grid):
        self.name = name
        self.grid = grid

        return self

    @property
    def label(self):
        return _(self._label) if self._label is not None else _(self.name)

    @property
    def template(self):
        raise NotImplementedError(
            "Each Column class should implement the template() property"
        )

    @property
    def bound(self):
        return self.name is not None and self.grid is not None

    def data(self, row):
        raise NotImplementedError(
            "Each Column class should implement the data() method"
        )

    def get_row_value(self, row, accessor):
        if not self.bound:
            raise ValueError("Cannot get row value for unbound column")

        if hasattr(self.grid, accessor) and callable(getattr(self.grid, accessor)):
            return getattr(self.grid, accessor)(self.grid, row)

        paths = accessor.split(".")
        row_value = row
        for path in paths:
            if hasattr(row_value, path):
                row_value = getattr(row_value, path)
            else:
                row_value = None
                break
        if row_value is not None:
            return row_value

        return None


class LeadingColumn(Column):
    """First column, with link, image and two rows of text"""

    def __init__(
        self,
        *,
        text,
        secondary_text=None,
        detail_url=None,
        image_src=None,
        icon=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.text = text
        self.secondary_text = secondary_text
        self.detail_url = detail_url
        self.image_src = image_src
        self.icon = icon

    @property
    def template(self):
        return "ui/datagrid/column_leading.html"

    def data(self, row):
        text_value = self.get_row_value(row, self.text)
        data = {"text": text_value, "single": self.secondary_text is None}
        if (
            self.detail_url is None
            and hasattr(row, "get_absolute_url")
            and callable(row.get_absolute_url)
        ):
            self.detail_url = "get_absolute_url"
        if self.detail_url is not None:
            data.update(detail_url=self.get_row_value(row, self.detail_url))
        if self.secondary_text is not None:
            secondary_text_value = self.get_row_value(row, self.secondary_text)
            data.update(
                secondary_text=secondary_text_value,
                empty=text_value is None and secondary_text_value is None,
            )
        else:
            data.update(empty=text_value is None)
        if self.image_src is not None:
            data.update(image_src=self.get_row_value(row, self.image_src))
        if self.icon is not None:
            data.update(icon=self.get_row_value(row, self.icon))

        data["image_alt"] = data.get("secondary_text", data["text"])

        return data


class TextColumn(Column):
    """Simple text column, with one or two rows"""

    def __init__(self, *, text=None, secondary_text=None, **kwargs):
        super().__init__(**kwargs)

        self.text = text
        self.secondary_text = secondary_text

    @property
    def template(self):
        return "ui/datagrid/column_text.html"

    def data(self, row):
        text_value = self.get_row_value(row, self.text)
        data = {
            "text": text_value,
            "single": self.secondary_text is None,
        }
        if self.secondary_text is not None:
            secondary_text_value = self.get_row_value(row, self.secondary_text)
            data.update(
                secondary_text=secondary_text_value,
                empty=text_value is None and secondary_text_value is None,
            )
        else:
            data.update(empty=text_value is None)
        return data


class DateColumn(Column):
    """Date column, with one or two rows"""

    def __init__(
        self, *, date=None, date_format="timesince", secondary_text=None, **kwargs
    ):
        super().__init__(**kwargs)

        self.date = date
        self.date_format = date_format
        self.secondary_text = secondary_text

    @property
    def template(self):
        return "ui/datagrid/column_date.html"

    def format_date(self, date):
        if date is None:
            return date

        if self.date_format == "timesince":
            if (timezone.now() - date).seconds < 60:
                return _("Just now")

            return f"{timesince(date)} {_('ago')}"
        else:
            return NotImplementedError('Only the "timesince" format is implemented')

    def data(self, row):
        data = {
            "date": self.format_date(self.get_row_value(row, self.date)),
            "single": self.secondary_text is None,
        }
        if self.secondary_text is not None:
            data.update(
                secondary_text=self.get_row_value(row, self.secondary_text),
            )

        return data


class CountryColumn(Column):
    """Country column"""

    def __init__(self, *, countries=None, **kwargs):
        super().__init__(**kwargs)

        self.countries = countries

    @property
    def template(self):
        return "ui/datagrid/column_countries.html"

    def data(self, row):
        return {"countries": self.get_row_value(row, self.countries)}


class LinkColumn(Column):
    def __init__(self, *, text, url=None, **kwargs):
        super().__init__(**kwargs, hide_label=True)
        self.text = text
        if url is None:
            url = "get_absolute_url"
        self.url = url

    @property
    def template(self):
        return "ui/datagrid/column_link.html"

    def data(self, row):
        return {"label": _(self.text), "url": self.get_row_value(row, self.url)}
