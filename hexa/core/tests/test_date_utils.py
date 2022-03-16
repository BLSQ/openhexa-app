from datetime import timedelta

from django.utils.dateparse import parse_datetime

from hexa.core.date_utils import date_format, duration_format
from hexa.core.test import TestCase


class DateUtilsTest(TestCase):
    def test_date_format(self):
        for date_time, expected_formatted_date_time in [
            (parse_datetime("2022-01-01T10:00:00Z"), "Jan 01, 10:00:00 (UTC)"),
        ]:
            self.assertEqual(expected_formatted_date_time, date_format(date_time))

    def test_duration_format(self):
        for time_delta, expected_formatted_time_delta in [
            (timedelta(hours=2, minutes=3, seconds=22), "2 hours, 3 minutes"),
            (timedelta(hours=1), "1 hour"),
            (timedelta(minutes=3, seconds=22), "3 minutes, 22 seconds"),
            (timedelta(minutes=1), "1 minute"),
            (timedelta(seconds=22), "22 seconds"),
            (timedelta(seconds=1), "1 second"),
        ]:
            self.assertEqual(expected_formatted_time_delta, duration_format(time_delta))
