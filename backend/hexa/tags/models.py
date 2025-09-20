from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

from hexa.core.models import Base


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
