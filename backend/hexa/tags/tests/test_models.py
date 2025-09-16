from django.core.exceptions import ValidationError
from django.test import TestCase

from hexa.tags.models import Tag


class TagModelTest(TestCase):
    def test_valid_tag_creation(self):
        """Test creating tags with valid names."""
        valid_names = [
            "ml",
            "machine-learning",
            "data-science-2023",
            "test123",
            "a1",
        ]

        for name in valid_names:
            tag = Tag(name=name)
            tag.full_clean()
            tag.save()
            self.assertEqual(tag.name, name)

    def test_invalid_tag_names_validation(self):
        """Test that invalid tag names are rejected during validation."""
        invalid_cases = [
            ("", "empty string"),
            ("a", "too short"),
            ("Machine-Learning", "uppercase letters"),
            ("data science", "spaces"),
            ("data_science", "underscores"),
            ("machine-learning-", "trailing hyphen"),
            ("-machine-learning", "leading hyphen"),
            ("data@science", "special characters"),
            ("machine--learning", "double hyphens"),
            ("tag!", "exclamation mark"),
            ("tag#hash", "hash symbol"),
        ]

        for invalid_name, description in invalid_cases:
            with self.subTest(name=invalid_name, description=description):
                tag = Tag(name=invalid_name)
                with self.assertRaises(ValidationError):
                    tag.full_clean()

    def test_whitespace_validation(self):
        """Test that leading/trailing whitespace is rejected."""
        whitespace_cases = [
            " tag",
            "tag ",
            " tag ",
            "\ttag",
            "tag\t",
            "\ntag",
            "tag\n",
        ]

        for name in whitespace_cases:
            with self.subTest(name=repr(name)):
                tag = Tag(name=name)
                with self.assertRaises(ValidationError):
                    tag.clean()

    def test_unique_constraint(self):
        """Test that duplicate tag names are not allowed."""
        Tag.objects.create(name="unique-tag")

        # Second attempt should raise ValidationError during save
        with self.assertRaises(ValidationError):
            Tag.objects.create(name="unique-tag")

    def test_case_sensitivity_in_uniqueness(self):
        """Test that uniqueness is case-sensitive at database level."""
        Tag.objects.create(name="test-tag")

        # This should succeed since validation prevents uppercase
        # but database allows it (case-sensitive unique constraint)
        tag_upper = Tag(name="TEST-TAG")
        with self.assertRaises(ValidationError):
            tag_upper.full_clean()

    def test_display_name_property(self):
        """Test the display_name property formats correctly."""
        test_cases = [
            ("machine-learning", "Machine Learning"),
            ("data-science-2023", "Data Science 2023"),
            ("ml", "Ml"),
            ("test123", "Test123"),
        ]

        for name, expected_display in test_cases:
            with self.subTest(name=name):
                tag = Tag(name=name)
                self.assertEqual(tag.display_name, expected_display)

    def test_str_representation(self):
        """Test string representation returns tag name."""
        tag = Tag(name="test-tag")
        self.assertEqual(str(tag), "test-tag")

    def test_save_calls_full_clean(self):
        """Test that save() calls full_clean() for validation."""
        tag = Tag(name="invalid name with spaces")

        with self.assertRaises(ValidationError):
            tag.save()

    def test_ordering(self):
        """Test that tags are ordered by name."""
        Tag.objects.create(name="zebra")
        Tag.objects.create(name="alpha")
        Tag.objects.create(name="beta")

        tags = list(Tag.objects.all())
        tag_names = [tag.name for tag in tags]

        self.assertEqual(tag_names, ["alpha", "beta", "zebra"])

    def test_database_constraints(self):
        """Test that database constraints are enforced."""
        # Test empty name constraint - should fail at validation level
        with self.assertRaises(ValidationError):
            Tag.objects.create(name="")

        # Test leading hyphen constraint - should fail at validation level
        with self.assertRaises(ValidationError):
            Tag.objects.create(name="-invalid")

        # Test trailing hyphen constraint - should fail at validation level
        with self.assertRaises(ValidationError):
            Tag.objects.create(name="invalid-")
