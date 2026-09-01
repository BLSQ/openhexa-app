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

        # Two call sites, both reached by ordinary fixture setup: creating an
        # organization provisions a git org, and creating a saved query or a static web
        # app commits to a repository. Neither may reach a real git server from a test,
        # so both are stubbed for the whole suite; tests that assert on git calls patch
        # `hexa.git.mixins.get_forgejo_client` themselves and override this.
        #
        # Patched where the name is used, not where it is defined: every caller does
        # `from hexa.git.forgejo import get_forgejo_client`, which binds the function in
        # the importing module at import time, so replacing the attribute on
        # `hexa.git.forgejo` would leave all of them pointing at the original. Nor is the
        # cached `forgejo._forgejo_client` singleton a shortcut worth taking: it looks
        # like one patch covering every caller, but `git.tests.test_forgejo` assigns that
        # global directly to exercise the caching and leaves it None, after which later
        # tests build a real client and reach the network.
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
