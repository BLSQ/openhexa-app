import datetime
import logging
import tempfile
from logging import FileHandler

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
        # Disable all existing handlers and set a simple file handler for tests
        # (To make sure that we can test logs but that they don't pollute the console output)
        logger = logging.getLogger()
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logging_file = f"{tempfile.gettempdir()}/{datetime.datetime.now().isoformat()}"
        logger.addHandler(FileHandler(logging_file))
