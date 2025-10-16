from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

from hexa.core.models import Base


class InvalidTag(Exception):
    """Raised when tag validation fails or tags don't exist."""

    pass


class Tag(Base):
    name = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        validators=[
            MinLengthValidator(
                2, message="Tag name must be at least 2 characters long"
            ),
            RegexValidator(
                r"^[a-z0-9]+(-[a-z0-9]+)*$",
                message="Tag name must contain only lowercase letters, numbers, and single hyphens",
            ),
        ],
        help_text="Lowercase alphanumeric characters and hyphens only",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(name__startswith="-"), name="tag_name_not_start_hyphen"
            ),
            models.CheckConstraint(
                check=~models.Q(name__endswith="-"), name="tag_name_not_end_hyphen"
            ),
        ]

    def clean(self):
        """Validate the tag name without modifying it."""
        super().clean()
        if self.name:
            if self.name != self.name.strip():
                raise ValidationError(
                    {"name": "Tag name cannot have leading or trailing whitespace."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        return self.name.replace("-", " ").title()

    @classmethod
    def _normalize_names(cls, tag_names: list[str]) -> list[str]:
        """Extract unique, cleaned tag names from input list.

        Args:
            tag_names: List of tag name strings (may contain duplicates/whitespace)

        Returns
        -------
            List of unique, stripped, non-empty tag names
        """
        return [name.strip() for name in set(tag_names) if name and name.strip()]

    @classmethod
    def from_names(cls, tag_names: list[str]):
        """Lookup existing tags by name. Raises InvalidTag if any missing.

        Args:
            tag_names: List of tag name strings

        Returns
        -------
            QuerySet of Tag instances

        Raises
        ------
            InvalidTag: If any tag names are not found in the database
        """
        if not tag_names:
            return cls.objects.none()

        unique_names = cls._normalize_names(tag_names)

        if not unique_names:
            return cls.objects.none()

        tags = cls.objects.filter(name__in=unique_names)
        found_names = set(tag.name for tag in tags)

        missing_names = set(unique_names) - found_names
        if missing_names:
            raise InvalidTag(f"Tags not found: {', '.join(sorted(missing_names))}")

        return tags

    @classmethod
    def validate_and_get_or_create(
        cls, tag_names: list[str]
    ) -> tuple[list["Tag"], bool]:
        """Validate tag names and get or create Tag instances.

        Args:
            tag_names: List of tag name strings

        Returns
        -------
            tuple: (list of Tag instances, has_error boolean)
                   has_error is True if validation failed
        """
        if not tag_names:
            return [], False

        unique_names = cls._normalize_names(tag_names)
        if not unique_names:
            return [], True

        tags = []
        try:
            for name in unique_names:
                tag, _ = cls.objects.get_or_create(name=name)
                tags.append(tag)
            return tags, False
        except Exception:
            return [], True
