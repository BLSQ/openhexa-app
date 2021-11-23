from __future__ import annotations

import typing

from django.core.paginator import Paginator
from django.db import models
from django.http import HttpRequest
from django.template import loader
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

from hexa.core.models import WithStatus
from hexa.ui.utils import get_item_value

DjangoModel = typing.TypeVar("DjangoModel", bound=models.Model)


class DatagridOptions:
    """Container for datagrid meta (config)"""

    def __init__(
        self,
        *,
        columns: typing.Sequence[Column],
        actions: typing.Sequence[Action] = None,
    ):
        self.columns = columns
        self.actions = actions


class DatagridMeta(type):
    """Metaclass for column registration"""

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, DatagridMeta)]
        if not parents:
            return new_class

        columns = []
        for column_name, column in [
            (k, v) for k, v in attrs.items() if isinstance(v, Column)
        ]:
            column.name = column_name
            columns.append(column)

        actions = []
        for action_name, action in [
            (k, v) for k, v in attrs.items() if isinstance(v, Action)
        ]:
            action.name = action_name
            actions.append(action)
        new_class._meta = DatagridOptions(columns=columns, actions=actions)

        return new_class


class Datagrid(metaclass=DatagridMeta):
    def __init__(
        self,
        queryset,
        *,
        paginate: bool = True,
        per_page: int = 20,
        page: int = 1,
        more_url: str = None,
        request: HttpRequest,
    ):
        self.paginator = Paginator(queryset, per_page)
        self.page = self.paginator.page(page)
        self.paginate = paginate
        self.more_url = more_url
        self.request = request

    def __str__(self):
        """Render the datagrid"""

        template = loader.get_template(self.template)

        return template.render(self.context())

    @property
    def template(self):
        return "ui/datagrid/datagrid.html"

    def context(self):
        rows = []
        for item in self.page:
            bound_columns = []
            for column in self._meta.columns:
                bound_columns.append(column.bind(grid=self, model=item))

            rows.append(bound_columns)
        return {
            "title": get_item_value(None, "title", container=self, exclude=Column),
            "actions": [action.bind(self) for action in self._meta.actions],
            "rows": rows,
            "columns": self._meta.columns,
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

    def __len__(self):
        return self.paginator.count


class Column:
    """Base column class (to be extended)"""

    def __init__(self, *, label=None, hide_label=False):
        self._label = label
        self.hide_label = hide_label
        self.name = None

    def bind(self, grid: Datagrid, model: DjangoModel):
        return BoundColumn(self, grid=grid, model=model)

    @property
    def label(self):
        return _(self._label) if self._label is not None else _(self.name)

    @property
    def template(self):
        raise NotImplementedError(
            "Each Column class should implement the template() property"
        )

    def context(self, model: DjangoModel, grid: Datagrid):
        raise NotImplementedError(
            "Each Column class should implement the context() method"
        )

    def get_value(self, model, accessor, container=None):
        return get_item_value(model, accessor, container=container, exclude=Column)


class BoundColumn:
    def __init__(
        self, unbound_column: Column, *, grid: Datagrid, model: DjangoModel
    ) -> None:
        self.unbound_column = unbound_column
        self.grid = grid
        self.model = model

    @property
    def name(self):
        return self.unbound_column.name

    def __str__(self):
        template = loader.get_template(self.unbound_column.template)

        return template.render(
            {
                **self.unbound_column.context(self.model, self.grid),
            },
            request=self.grid.request,
        )


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
        translate=True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.text = text
        self.secondary_text = secondary_text
        self.detail_url = detail_url
        self.image_src = image_src
        self.icon = icon
        self.translate = translate

    @property
    def template(self):
        return "ui/datagrid/column_leading.html"

    def context(self, model: DjangoModel, grid: Datagrid):
        text_value = self.get_value(model, self.text, container=grid)
        data = {
            "text": text_value,
            "single": self.secondary_text is None,
            "translate": self.translate,
        }
        if (
            self.detail_url is None
            and hasattr(model, "get_absolute_url")
            and callable(model.get_absolute_url)
        ):
            self.detail_url = "get_absolute_url"
        if self.detail_url is not None:
            data.update(
                detail_url=self.get_value(model, self.detail_url, container=grid)
            )
        if self.secondary_text is not None:
            secondary_text_value = self.get_value(
                model, self.secondary_text, container=grid
            )
            data.update(
                secondary_text=secondary_text_value,
                empty=text_value is None and secondary_text_value is None,
            )
        else:
            data.update(empty=text_value is None)
        if self.image_src is not None:
            data.update(image_src=self.get_value(model, self.image_src, container=grid))
        if self.icon is not None:
            data.update(icon=self.get_value(model, self.icon, container=grid))

        data["image_alt"] = data.get("secondary_text", data["text"])

        return data


class TextColumn(Column):
    """Simple text column, with one or two rows"""

    def __init__(self, *, text=None, secondary_text=None, translate=True, **kwargs):
        super().__init__(**kwargs)

        self.text = text
        self.secondary_text = secondary_text
        self.translate = translate

    @property
    def template(self):
        return "ui/datagrid/column_text.html"

    def context(self, model: DjangoModel, grid: Datagrid):
        text_value = self.get_value(model, self.text, container=grid)
        data = {
            "text": text_value,
            "single": self.secondary_text is None,
            "translate": self.translate,
        }
        if self.secondary_text is not None:
            secondary_text_value = self.get_value(
                model, self.secondary_text, container=grid
            )
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

    def context(self, model: DjangoModel, grid: Datagrid):
        data = {
            "date": self.format_date(self.get_value(model, self.date, container=grid)),
            "single": self.secondary_text is None,
        }
        if self.secondary_text is not None:
            data.update(
                secondary_text=self.get_value(
                    model, self.secondary_text, container=grid
                ),
            )

        return data


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

    def context(self, model: DjangoModel, grid: Datagrid):
        return {
            "label": _(self.text),
            "url": self.get_value(model, self.url, container=grid),
        }


class TagColumn(Column):
    def __init__(self, *, value=None, max_items=2, **kwargs):
        super().__init__(**kwargs)

        self.value = value
        self.max_items = max_items

    @property
    def template(self):
        return "ui/datagrid/column_tag.html"

    def tags_data(self, model: DjangoModel, grid: Datagrid):
        return [
            {"label": t.name}
            for t in self.get_value(model, self.value, container=Datagrid)
        ]

    def context(self, model: DjangoModel, grid: Datagrid):
        tags_data = self.tags_data(model, grid)

        return {
            "tags": tags_data,
            "slice": f":{self.max_items}",
            "left_out": max(0, len(tags_data) - self.max_items),
        }


class CountryColumn(TagColumn):
    def tags_data(self, model: DjangoModel, grid: Datagrid):
        return [
            {"label": c.name, "short_label": c.alpha3, "image": c.flag}
            for c in self.get_value(model, self.value, container=Datagrid)
        ]


class StatusColumn(Column):
    def __init__(self, *, value=None, **kwargs):
        super().__init__(**kwargs)

        self.value = value

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

    @property
    def template(self):
        return "ui/datagrid/column_status.html"

    def context(self, model: DjangoModel, grid: Datagrid):
        status = self.get_value(model, self.value, container=Datagrid)

        return {
            "color": self.COLOR_MAPPINGS.get(status),
            "label": self.LABEL_MAPPINGS.get(status),
        }


class Action:
    def __init__(self, *, label, url, icon=None, method="post"):
        self.label = label
        self.icon = icon
        self.url = url
        self.method = method

    def bind(self, datagrid: Datagrid):
        return BoundAction(self, datagrid=datagrid)

    def get_value(self, model, accessor, container=None):
        return get_item_value(
            model, accessor, container=container, exclude=(Datagrid, Column)
        )

    @property
    def template(self):
        return "ui/datagrid/action.html"

    def context(self, grid: Datagrid):
        return {
            "url": self.get_value(None, self.url, container=grid),
            "label": _(self.label),
            "icon": self.icon,
            "method": self.method,
        }


class BoundAction:
    def __init__(self, unbound_action: Action, *, datagrid: Datagrid):
        self.unbound_action = unbound_action
        self.datagrid = datagrid

    def __str__(self):
        template = loader.get_template(self.unbound_action.template)

        return template.render(
            self.unbound_action.context(self.datagrid),
            request=self.datagrid.request,
        )
