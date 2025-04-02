from django.contrib.gis.db import models
from django_countries.fields import Country as DjangoCountry

from hexa.core.models import Base

WHO_REGION_NAMES = {
    "AMRO": "Region of the Americas",
    "AFRO": "African Region",
    "EMRO": "Eastern Mediterranean Region",
    "EURO": "European Region",
    "WPRO": "Western Pacific Region",
    "SEARO": "South-East Asian Region",
}


class WHORegion(models.TextChoices):
    AMRO = "AMRO"
    AFRO = "AFRO"
    EMRO = "EMRO"
    EURO = "EURO"
    WPRO = "WPRO"
    SEARO = "SEARO"


class Country(Base):
    name = models.TextField()
    code = models.CharField(max_length=2)
    alpha3 = models.CharField(max_length=3)

    # WHO Info
    region = models.CharField(max_length=50, choices=WHORegion.choices)
    default_crs = models.IntegerField()
    simplified_extent = models.GeometryField()

    def get_who_info(self):
        return {
            "region": {
                "code": self.region,
                "name": WHO_REGION_NAMES[self.region],
            },
            "default_crs": self.default_crs,
            "simplified_extent": self.simplified_extent.tuple,
        }

    @property
    def flag(self):
        return DjangoCountry(self.code).flag


class WHOBoundary(Base):
    name = models.TextField()
    country = models.ForeignKey(Country, related_name="zones", on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "WHOBoundary", related_name="childrens", on_delete=models.SET_NULL, null=True
    )
    administrative_level = models.IntegerField()
    extent = models.GeometryField()
