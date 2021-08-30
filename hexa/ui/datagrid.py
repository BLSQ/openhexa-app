from django.template import loader
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
        column_config = [
            {
                "label": _(column.label if column.label is not None else column_name),
                "template": column.template,
            }
            for column_name, column in self._meta.columns.items()
        ]
        row_data = []
        for row in self.queryset:
            single_row_data = []
            for column_name, column in self._meta.columns.items():
                single_row_data.append(
                    {"template": column.template, "data": column.data(row)}
                )

            row_data.append(single_row_data)

        context = {"rows": row_data, "columns": column_config}

        return template.render(context)


class Column:
    """Base column class (to be extended)"""

    def __init__(self, *, label=None):
        self.label = label
        self.name = None
        self.grid = None

    def bind(self, name, grid):
        self.name = name
        self.grid = grid

        return self

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

        paths = accessor.split(".")
        value = row
        for path in paths:
            value = getattr(value, path)

        return value


class LeadingColumn(Column):
    """First column, with link, image and two rows of text"""

    def __init__(
        self, *, image_src=None, main_text=None, secondary_text=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.image_src = image_src
        self.main_text = main_text
        self.secondary_text = secondary_text

    @property
    def template(self):
        return "ui/datagrid/column_leading.html"

    def data(self, row):
        return {
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


class LinkColumn(Column):
    def __init__(self, *, text, url, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.url = url
