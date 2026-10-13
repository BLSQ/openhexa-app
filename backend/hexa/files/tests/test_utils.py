from unittest import TestCase

from hexa.files.utils import is_public_path, is_safe_path

UNSAFE_PATHS = [
    "/etc/passwd",
    "/var/log/syslog",
    "..",
    "../etc/passwd",
    "../../secret",
    "foo/../..",
    "foo/bar/../../../secret",
    "foo/./../../secret",
    "foo//../../secret",
    "//etc/passwd",
    "foo\x00bar",
    "~/secret",
]

SAFE_PATHS = [
    "file.txt",
    "foo/bar/baz.txt",
    ".",
    "",
    ".hidden",
    "foo/../bar",
    "foo/./bar",
    "foo//bar",
    "a/b/c/d/e/f.txt",
    "..hidden",
    "...hidden",
    "foo/..bar",
]


class IsSafePathTest(TestCase):
    def test_unsafe_paths(self):
        for path in UNSAFE_PATHS:
            with self.subTest(path=path):
                self.assertFalse(is_safe_path(path))

    def test_safe_paths(self):
        for path in SAFE_PATHS:
            with self.subTest(path=path):
                self.assertTrue(is_safe_path(path))


class IsPublicPathTest(TestCase):
    def test_files_inside_the_public_folder(self):
        for path in ["public/data.json", "public/tiles/map.pmtiles", "public//a.txt"]:
            with self.subTest(path=path):
                self.assertTrue(is_public_path(path))

    def test_everything_else(self):
        for path in [
            "",
            "public",
            "public/",
            "publicity/data.json",
            "data/public/data.json",
            "secret.csv",
            "./public",
        ]:
            with self.subTest(path=path):
                self.assertFalse(is_public_path(path))
