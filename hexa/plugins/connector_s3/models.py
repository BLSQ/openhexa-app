from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from s3fs import S3FileSystem

from hexa.catalog.models import Content, Datasource, CatalogIndex


class BucketQuerySet(models.QuerySet):
    def for_user(self, user):
        if not (user.is_active and user.is_superuser):
            return self.none()

        return self


class Bucket(Datasource):
    class Meta:
        verbose_name = "S3 Bucket"
        ordering = ("name",)

    s3_name = models.CharField(max_length=200)
    s3_access_key_id = models.CharField(max_length=200)  # TODO: secure
    s3_secret_access_key = models.CharField(max_length=200)  # TODO: secure

    objects = BucketQuerySet.as_manager()

    def sync(self):
        """Sync the bucket by querying the DHIS2 API"""

        fs = S3FileSystem(key=self.s3_access_key_id, secret=self.s3_secret_access_key)
        ls = fs.ls(self.s3_name + "/", detail=True)
        foo = "bar"

        return

        # Sync data elements
        with transaction.atomic():

            # Flag the datasource as synced
            self.last_synced_at = timezone.now()
            self.save()

        # return data_element_results + indicator_type_results + indicator_results

    @property
    def content_summary(self):
        if self.last_synced_at is None:
            return ""

        return _(
            "%(data_element_count)s data elements, %(indicator_count)s indicators"
        ) % {
            "data_element_count": self.dataelement_set.count(),
            "indicator_count": self.indicator_set.count(),
        }

    def index(self):
        CatalogIndex.objects.create_or_update(
            indexed_object=self,
            owner=self.owner,
            name=self.name,
            short_name=self.short_name,
            description=self.description,
            countries=self.countries,
            content_summary=self.content_summary,
            last_synced_at=self.last_synced_at,
            detail_url=reverse("connector_s3:datasource_detail", args=(self.pk,)),
        )


# class Object(Content):
#     class Meta:
#         ordering = ["s3_name"]
#
#     instance = models.ForeignKey("Instance", null=False, on_delete=models.CASCADE)
#     s3_id = models.CharField(max_length=200)
#     s3_name = models.CharField(max_length=200)
#
#     @property
#     def display_name(self):
#         return self.s3_name
