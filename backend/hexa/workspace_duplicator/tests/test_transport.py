import logging

from django.test import SimpleTestCase

from hexa.workspace_duplicator import transport


class DebugLoggingTest(SimpleTestCase):
    def setUp(self):
        self.httpx = logging.getLogger("httpx")
        self.httpcore = logging.getLogger("httpcore")
        # Pin a known starting state and restore it afterwards, so these tests
        # neither depend on nor perturb global logging / DEBUG state.
        saved = {
            "DEBUG": transport.DEBUG,
            "httpx": self.httpx.level,
            "httpcore": self.httpcore.level,
        }
        transport.DEBUG = False
        self.httpx.setLevel(logging.INFO)
        self.httpcore.setLevel(logging.INFO)

        def restore():
            transport.DEBUG = saved["DEBUG"]
            self.httpx.setLevel(saved["httpx"])
            self.httpcore.setLevel(saved["httpcore"])

        self.addCleanup(restore)

    def test_enabled_turns_on_debug_inside_block(self):
        with transport.debug_logging(True):
            self.assertTrue(transport.DEBUG)
            self.assertEqual(self.httpx.level, logging.DEBUG)
            self.assertEqual(self.httpcore.level, logging.DEBUG)

    def test_disabled_quiets_http_loggers_inside_block(self):
        with transport.debug_logging(False):
            self.assertFalse(transport.DEBUG)
            self.assertEqual(self.httpx.level, logging.WARNING)
            self.assertEqual(self.httpcore.level, logging.WARNING)

    def test_restores_previous_state_on_exit(self):
        with transport.debug_logging(True):
            pass
        self.assertFalse(transport.DEBUG)
        self.assertEqual(self.httpx.level, logging.INFO)
        self.assertEqual(self.httpcore.level, logging.INFO)

    def test_restores_state_even_when_block_raises(self):
        with self.assertRaises(ValueError):
            with transport.debug_logging(True):
                raise ValueError("boom")
        self.assertFalse(transport.DEBUG)
        self.assertEqual(self.httpx.level, logging.INFO)
        self.assertEqual(self.httpcore.level, logging.INFO)

    def test_does_not_leak_across_calls(self):
        with transport.debug_logging(True):
            pass
        # A later default-off run must see the restored state, not the previous
        # block's enabled state (the leak this context manager guards against).
        with transport.debug_logging(False):
            self.assertFalse(transport.DEBUG)
        self.assertFalse(transport.DEBUG)
