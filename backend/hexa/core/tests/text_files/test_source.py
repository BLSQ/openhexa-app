from django.test import SimpleTestCase

from hexa.core.text_files import decode_text


class DecodeTextTest(SimpleTestCase):
    def test_text(self):
        self.assertEqual(decode_text("héllo".encode()), "héllo")

    def test_binary(self):
        self.assertIsNone(decode_text(b"\x89PNG\x00"))
        self.assertIsNone(decode_text(b"\xff\xfe"))
