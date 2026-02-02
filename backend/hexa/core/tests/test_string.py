from hexa.core.string import generate_filename, generate_short_name, remove_whitespace
from hexa.core.test import TestCase


class StringTest(TestCase):
    def test_remove_whitespace(self):
        self.assertEqual("", remove_whitespace("\t \n \r \t"))

    def test_generate_filename(self):
        self.assertEqual("test_file.csv", generate_filename("TeST __  - file.csv"))

    def test_generate_short_name_multi_word(self):
        self.assertEqual(generate_short_name("World Health Organization"), "WHO")

    def test_generate_short_name_single_word(self):
        self.assertEqual(generate_short_name("Bluesquare"), "BLUES")

    def test_generate_short_name_long_multi_word(self):
        self.assertEqual(
            generate_short_name("United Nations Development Programme Agency"),
            "UNDPA",
        )

    def test_generate_short_name_special_characters(self):
        self.assertEqual(generate_short_name("Org-123 Test!"), "OT")

    def test_generate_short_name_fallback(self):
        self.assertEqual(generate_short_name("123"), "ORG")

    def test_generate_short_name_leading_digits(self):
        self.assertEqual(generate_short_name("123Bluesquare"), "BLUES")
