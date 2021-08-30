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
    def __init__(self, queryset):
        self.queryset = queryset

    def __str__(self):
        """Render the datagrid"""

        template = loader.get_template("ui/datagrid/datagrid.html")
        row_data = []
        for row in self.queryset:
            single_row_data = []
            for column_name, column in self._meta.columns.items():
                single_row_data.append(
                    {"template": column.template, "data": column.data(row)}
                )

            row_data.append(single_row_data)

        context = {"rows": row_data, "columns": self._meta.columns.values()}

        return template.render(context)


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
        self, *, main_text, secondary_text, detail_url=None, image_src=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.main_text = main_text
        self.secondary_text = secondary_text
        self.detail_url = detail_url
        self.image_src = image_src

    @property
    def template(self):
        return "ui/datagrid/column_leading.html"

    def data(self, row):
        return {
            "detail_url": self.get_row_value(row, self.detail_url),
            "main_text": self.get_row_value(row, self.main_text),
            "secondary_text": self.get_row_value(row, self.secondary_text),
            "image_src": self.get_row_value(row, self.image_src),
        }


class TextColumn(Column):
    """Simple text column, with one or two rows"""

    def __init__(self, *, text=None, main_text=None, secondary_text=None, **kwargs):
        super().__init__(**kwargs)

        # just "text"
        if text is not None and (main_text is None and secondary_text is None):
            self.text = text
            self.main_text = None
            self.secondary_text = None
        # "main" and "secondary" text
        elif text is None and (main_text is not None and secondary_text is not None):
            self.main_text = main_text
            self.secondary_text = secondary_text
            self.text = None
        else:
            raise ValueError(
                'Text columns either have a "text" property or both "main_text" and "secondary_text"'
            )

    @property
    def template(self):
        return "ui/datagrid/column_text.html"

    def data(self, row):
        if self.text is not None:
            return {"text": self.get_row_value(row, self.text), "single": True}

        return {
            "main_text": self.get_row_value(row, self.main_text),
            "secondary_text": self.get_row_value(row, self.secondary_text),
            "single": False,
        }


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
        data = {"date": self.format_date(self.get_row_value(row, self.date))}
        if self.secondary_text is not None:
            data.update(
                secondary_text=self.get_row_value(row, self.secondary_text),
                single=False,
            )
        else:
            data.update(single=True)

        return data


class LinkColumn(Column):
    def __init__(self, *, text, url, **kwargs):
        super().__init__(**kwargs, hide_label=True)
        self.text = text
        self.url = url

    @property
    def template(self):
        return "ui/datagrid/column_link.html"

    def data(self, row):
        return {"label": _(self.text), "url": self.get_row_value(row, self.url)}
