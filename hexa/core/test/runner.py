from django.conf import settings
from django.test.runner import DiscoverRunner as BaseDiscoverRunner


class DiscoverRunner(BaseDiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        # ManifestStaticFileStorage & friends are not well-suited for tests, as they would required
        # collectstatic to be run before each test run
        settings.STATICFILES_STORAGE = (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
        )
        settings.SAVE_REQUESTS = True
