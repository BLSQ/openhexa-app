from hexa.core.mimetypes import guess_extension, guess_type
from hexa.core.test import TestCase


class MimetypesTest(TestCase):
    def test_guess_type(self):
        for url, expected_type in [
            ("file.csv", "text/csv"),
            ("file.json", "application/json"),
            ("file.geojson", "application/geo+json"),
            ("file.gpkg", "application/geopackage+sqlite3"),
            ("file.tif", "image/tiff"),
        ]:
            self.assertEqual(expected_type, guess_type(url)[0])

    def test_guess_extension(self):
        for type, expected_extension in [
            ("text/csv", ".csv"),
            ("application/json", ".json"),
            ("application/geo+json", ".geojson"),
            ("application/geopackage+sqlite3", ".gpkg"),
            ("image/tiff", ".tiff"),
        ]:
            self.assertEqual(expected_extension, guess_extension(type))
