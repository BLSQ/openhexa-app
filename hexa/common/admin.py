def country_list(obj):
    """List display helper for country fields"""

    return ",".join(country.alpha3 for country in obj.countries)


country_list.short_description = "Countries"
