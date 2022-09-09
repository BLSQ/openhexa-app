from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.urls import reverse
from django.utils.http import urlencode

from hexa.ui import datacard

from .models import Collection, CollectionElement


class CollectionsSection(datacard.Section):
    title = "Collections"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def template(self):
        return "data_collections/datacard/section_collections.html"

    @property
    def is_editable(self):
        # TODO: Link this to a user perm
        return True

    def is_enabled(self, request: HttpRequest, model):
        return request.user.has_feature_flag("collections")

    def context(self, model, card):
        content_type = ContentType.objects.get_for_model(model)
        params = urlencode(
            {
                "redirect": card.request.path,
                "objectId": model.id,
                "app": content_type.app_label,
                "model": content_type.model,
            }
        )

        manage_url = f"{reverse('data_collections:manage_collections')}?{params}"

        elements = (
            CollectionElement.objects.filter_for_user(card.request.user)
            .filter_for_object(model)
            .order_by("-updated_at")
            .select_related("collection")
        )
        return {
            "manage_url": manage_url,
            "collections": [
                {
                    "name": element.collection.name,
                    "url": element.collection.get_absolute_url(),
                }
                for element in elements
            ],
        }

    class Meta:
        model = Collection
