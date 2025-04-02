from hexa.core.string import generate_filename, remove_whitespace
from hexa.core.test import TestCase


class StringTest(TestCase):
    def test_remove_whitespace(self):
        self.assertEqual("", remove_whitespace("\t \n \r \t"))

    def test_generate_filename(self):
        self.assertEqual("test_file.csv", generate_filename("TeST __  - file.csv"))
