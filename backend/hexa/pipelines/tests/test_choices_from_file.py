from hexa.core.test import TestCase
from hexa.pipelines.choices_from_file import (
    _extract_from_data,
    _parse_csv,
    _parse_json,
    _parse_yaml,
)


class ParseCsvTest(TestCase):
    PATH = "choices.csv"

    def test_single_column_returns_values(self):
        text = "district\nNairobi\nMombasa\nKisumu\n"
        self.assertEqual(
            _parse_csv(text, None, self.PATH), ["Nairobi", "Mombasa", "Kisumu"]
        )

    def test_multi_column_with_column_specified(self):
        text = "code,name\nNBI,Nairobi\nMSA,Mombasa\n"
        self.assertEqual(_parse_csv(text, "code", self.PATH), ["NBI", "MSA"])

    def test_multi_column_no_column_raises(self):
        text = "code,name\nNBI,Nairobi\n"
        with self.assertRaisesRegex(ValueError, "multiple columns"):
            _parse_csv(text, None, self.PATH)

    def test_missing_column_raises(self):
        text = "code\nNBI\n"
        with self.assertRaisesRegex(ValueError, "not found"):
            _parse_csv(text, "nonexistent", self.PATH)

    def test_empty_file_raises(self):
        with self.assertRaisesRegex(ValueError, "empty or has no header row"):
            _parse_csv("", None, self.PATH)

    def test_empty_string_values_are_filtered(self):
        text = "district\nNairobi\n\nKisumu\n"
        self.assertEqual(_parse_csv(text, None, self.PATH), ["Nairobi", "Kisumu"])

    def test_none_values_are_filtered(self):
        # DictReader yields None for fields beyond the header column count
        text = "code,name\nNBI\nMSA,Mombasa\n"
        self.assertEqual(_parse_csv(text, "name", self.PATH), ["Mombasa"])

    def test_header_only_returns_empty_list(self):
        text = "district\n"
        self.assertEqual(_parse_csv(text, None, self.PATH), [])


class ExtractFromDataTest(TestCase):
    PATH = "data.json"
    FMT = "JSON"

    def test_flat_scalar_list(self):
        self.assertEqual(
            _extract_from_data(["a", "b", "c"], None, self.PATH, self.FMT),
            ["a", "b", "c"],
        )

    def test_flat_scalar_list_coerces_to_str(self):
        self.assertEqual(
            _extract_from_data([1, 2, 3], None, self.PATH, self.FMT),
            ["1", "2", "3"],
        )

    def test_empty_list_returns_empty(self):
        self.assertEqual(_extract_from_data([], None, self.PATH, self.FMT), [])

    def test_objects_single_key_auto_detected(self):
        data = [{"code": "NBI"}, {"code": "MSA"}]
        self.assertEqual(
            _extract_from_data(data, None, self.PATH, self.FMT), ["NBI", "MSA"]
        )

    def test_objects_multi_key_with_column(self):
        data = [
            {"code": "NBI", "name": "Nairobi"},
            {"code": "MSA", "name": "Mombasa"},
        ]
        self.assertEqual(
            _extract_from_data(data, "code", self.PATH, self.FMT), ["NBI", "MSA"]
        )

    def test_objects_multi_key_no_column_raises(self):
        data = [{"code": "NBI", "name": "Nairobi"}]
        with self.assertRaisesRegex(ValueError, "multiple keys"):
            _extract_from_data(data, None, self.PATH, self.FMT)

    def test_mixed_list_dict_then_scalar_raises(self):
        data = [{"code": "NBI"}, "Mombasa"]
        with self.assertRaisesRegex(ValueError, "mix of objects and scalar values"):
            _extract_from_data(data, None, self.PATH, self.FMT)

    def test_mixed_list_scalar_then_dict_raises(self):
        data = ["Nairobi", {"code": "MSA"}]
        with self.assertRaisesRegex(ValueError, "mix of objects and scalar values"):
            _extract_from_data(data, None, self.PATH, self.FMT)

    def test_dict_wrapper_single_key(self):
        data = {"choices": ["a", "b", "c"]}
        self.assertEqual(
            _extract_from_data(data, None, self.PATH, self.FMT), ["a", "b", "c"]
        )

    def test_dict_wrapper_multi_key_with_column(self):
        data = {"codes": ["NBI", "MSA"], "names": ["Nairobi", "Mombasa"]}
        self.assertEqual(
            _extract_from_data(data, "codes", self.PATH, self.FMT), ["NBI", "MSA"]
        )

    def test_dict_wrapper_multi_key_no_column_raises(self):
        data = {"codes": ["NBI"], "names": ["Nairobi"]}
        with self.assertRaisesRegex(ValueError, "multiple keys"):
            _extract_from_data(data, None, self.PATH, self.FMT)

    def test_dict_wrapper_missing_key_raises(self):
        data = {"choices": ["a"]}
        with self.assertRaisesRegex(ValueError, "not found"):
            _extract_from_data(data, "nonexistent", self.PATH, self.FMT)

    def test_non_list_non_dict_raises(self):
        with self.assertRaisesRegex(ValueError, "top-level array"):
            _extract_from_data("just a string", None, self.PATH, self.FMT)

    def test_objects_missing_column_key_are_skipped(self):
        data = [{"code": "NBI"}, {"name": "Mombasa"}]
        self.assertEqual(
            _extract_from_data(data, "code", self.PATH, self.FMT), ["NBI"]
        )


class ParseJsonTest(TestCase):
    PATH = "data.json"

    def test_flat_array(self):
        self.assertEqual(_parse_json('["a", "b"]', None, self.PATH), ["a", "b"])

    def test_invalid_json_raises(self):
        with self.assertRaisesRegex(ValueError, "Could not parse JSON"):
            _parse_json("{not valid json", None, self.PATH)


class ParseYamlTest(TestCase):
    PATH = "data.yaml"

    def test_flat_sequence(self):
        self.assertEqual(_parse_yaml("- a\n- b\n", None, self.PATH), ["a", "b"])

    def test_invalid_yaml_raises(self):
        with self.assertRaisesRegex(ValueError, "Could not parse YAML"):
            _parse_yaml("key: [unclosed", None, self.PATH)
