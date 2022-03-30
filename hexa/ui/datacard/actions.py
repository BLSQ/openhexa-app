from __future__ import annotations

import typing

from django.http import HttpRequest
from django.template import loader
from django.utils.translation import gettext_lazy as _

import hexa.ui.datacard
from hexa.ui.utils import get_item_value

from .base import DatacardComponent


class Action(DatacardComponent):
    def __init__(
        self,
        *,
        label: str,
        url: str,
        icon: typing.Optional[str] = None,
        method: str = "post",
        open_in_new_tab: bool = False,
        primary: bool = True,
        enabled_when: typing.Optional[typing.Callable] = None,
    ):
        if open_in_new_tab and method.lower() != "get":
            raise ValueError(
                '"open_in_new_tab" can only be set to true if "method" is "get"'
            )

        self.label = label
        self.icon = icon
        self.url = url
        self.method = method
        self.open_in_new_tab = open_in_new_tab
        self.primary = primary
        self.enabled_when = enabled_when

    def bind(self, datacard: hexa.ui.datacard.Datacard):
        return BoundAction(self, datacard=datacard)

    def get_value(self, model, accessor, container=None):
        return get_item_value(
            model, accessor, container=container, exclude=DatacardComponent
        )

    @property
    def template(self):
        return "ui/datacard/action.html"

    def context(self, model, card: hexa.ui.datacard.Datacard):
        return {
            "url": self.get_value(model, self.url, container=card),
            "label": _(self.label),
            "icon": self.icon,
            "method": self.method,
            "open_in_new_tab": self.open_in_new_tab,
            "primary": self.primary,
        }


class BoundAction:
    def __init__(self, unbound_action: Action, *, datacard: hexa.ui.datacard.Datacard):
        self.unbound_action = unbound_action
        self.datacard = datacard

    def is_enabled(self, request: HttpRequest):
        if self.unbound_action.enabled_when:
            return self.unbound_action.enabled_when(request, self.datacard.model)

        return True

    def __str__(self):
        template = loader.get_template(self.unbound_action.template)

        return template.render(
            self.unbound_action.context(self.datacard.model, self.datacard),
            request=self.datacard.request,
        )
