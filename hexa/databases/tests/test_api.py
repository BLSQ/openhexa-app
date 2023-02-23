import re

from django.core.exceptions import ValidationError

from hexa.core.test import TestCase
from hexa.databases.api import create_database, format_db_name


class DatabaseAPITest(TestCase):
    def test_format_db_name(self):
        db_name = "RDC_POLIO_PROJECT"
        self.assertEqual(len(db_name), len(format_db_name(db_name)))

        # test with a name with length superior to 31
        db_name = "THIS_IS_A_VERY_LONG_TEXT_WITH_MORE_THAN_31_LETTERS"
        self.assertTrue(len(format_db_name(db_name)) <= 31)

        # test with a name beginning with a character
        db_name = "1rwandaProject"
        self.assertFalse(re.match("^[0-9]", format_db_name(db_name)))

    def test_create_database_raise_error(self):
        bad_input = "1_invalid_db_name"
        password = "password"
        with self.assertRaises(ValidationError):
            create_database(bad_input, password)
