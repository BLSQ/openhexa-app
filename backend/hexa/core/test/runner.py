import datetime
import logging
import tempfile
from logging import FileHandler
from unittest.mock import patch

from django.conf import settings
from django.test.runner import DiscoverRunner as BaseDiscoverRunner

from hexa.git.testutils import make_git_client_mock


class DiscoverRunner(BaseDiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)

        # Ordinary fixture setup reaches the git server twice over — an organization
        # provisions a git org, a saved query or web app commits — so both call sites
        # are stubbed suite-wide. Patched where the name is used, not where it is
        # defined: callers bind it at import time. Patching the cached
        # `forgejo._forgejo_client` instead is not a shortcut — `test_forgejo` assigns
        # that global directly and leaves it None.
        self._forgejo_patchers = [
            patch(target, return_value=make_git_client_mock())
            for target in (
                "hexa.user_management.models.get_forgejo_client",
                "hexa.git.mixins.get_forgejo_client",
            )
        ]
        for patcher in self._forgejo_patchers:
            patcher.start()
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

    def teardown_test_environment(self, **kwargs):
        for patcher in self._forgejo_patchers:
            patcher.stop()
        super().teardown_test_environment(**kwargs)
