from hexa.app import CoreAppConfig


class DataStudioConfig(CoreAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hexa.data_studio"
    label = "data_studio"

    # Public saved queries are exported by visitors without an account.
    ANONYMOUS_URLS = ["data_studio:download_saved_query_csv"]
