from __future__ import annotations

from django.template import loader
from django.utils.translation import ugettext_lazy as _

import hexa.ui.datacard.legacy
from hexa.ui.utils import get_item_value

from .base import DatacardComponent


class Action(DatacardComponent):
    def __init__(self, *, label, url, icon=None, method="post"):
        self.label = label
        self.icon = icon
        self.url = url
        self.method = method

    def bind(self, datacard: hexa.ui.datacard.legacy.LegacyDatacard):
        return BoundAction(self, datacard=datacard)

    def get_value(self, model, accessor, container=None):
        return get_item_value(
            model, accessor, container=container, exclude=DatacardComponent
        )

    @property
    def template(self):
        return "ui/datacard/action.html"

    def context(self, model, card: hexa.ui.datacard.legacy.LegacyDatacard):
        return {
            "url": self.get_value(model, self.url, container=card),
            "label": _(self.label),
            "icon": self.icon,
            "method": self.method,
        }


class BoundAction:
    def __init__(
        self,
        unbound_action: Action,
        *,
        datacard: hexa.ui.datacard.legacy.LegacyDatacard
    ):
        self.unbound_action = unbound_action
        self.datacard = datacard

    def __str__(self):
        template = loader.get_template(self.unbound_action.template)

        return template.render(
            self.unbound_action.context(self.datacard.model, self.datacard),
            request=self.datacard.request,
        )
