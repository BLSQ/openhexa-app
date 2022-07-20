from django.apps import AppConfig

from hexa.plugins.app import CoreAppConfig


class CountriesConfig(AppConfig, CoreAppConfig):
    name = "hexa.countries"
    label = "countries"
    verbose_name = "Countries"
