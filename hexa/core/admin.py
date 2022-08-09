from django.contrib import admin
from .models.customcredentials import Credentials

@admin.display
def country_list(obj):
    """List display helper for country fields"""

    country_count = len(obj.countries)
    max_count = 3
    country_list_string = ", ".join(
        country.name for country in obj.countries[:max_count]
    )
    if country_count > max_count:
        country_list_string += f" (+{country_count - max_count})"

    return country_list_string

@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("user", 'name', "value")