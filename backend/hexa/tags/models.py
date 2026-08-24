from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from slugify import slugify

from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet


class InvalidTag(Exception):
    """Raised when tag validation fails or tags don't exist."""

    pass


class TagQuerySet(BaseQuerySet):
    def get_or_create_from_names(
        self, names: list[str], *, slugify_names: bool = False
    ) -> list["Tag"]:
        tags = []
        for name in names:
            if slugify_names:
                resolved = slugify(name)
                if not resolved:
                    raise InvalidTag(f"'{name}' cannot be converted to a valid tag")
            else:
                resolved = name.strip() if isinstance(name, str) else ""

            try:
                tag, _ = self.get_or_create(name=resolved)
            except ValidationError as e:
                raise InvalidTag(f"'{name}' is not a valid tag name") from e

            if tag not in tags:
                tags.append(tag)
        return tags


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

    objects = TagQuerySet.as_manager()

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
    def from_names(cls, tag_names: list[str]):
        if not tag_names:
            return cls.objects.none()

        unique_names = [
            name.strip() for name in set(tag_names) if name and name.strip()
        ]

        if not unique_names:
            return cls.objects.none()

        tags = cls.objects.filter(name__in=unique_names)
        found_names = set(tag.name for tag in tags)

        missing_names = set(unique_names) - found_names
        if missing_names:
            raise InvalidTag(f"Tags not found: {', '.join(sorted(missing_names))}")

        return tags
