# Generated by Django 4.0.4 on 2022-04-13 05:58

import django.db.models.deletion
import django.db.models.expressions
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("user_management", "0009_user_management_to_identity_1"),
        ("connector_dhis2", "0026_remove_dhis2_extracts"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="instancepermission",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="instancepermission",
            name="mode",
            field=models.CharField(
                choices=[
                    ("OWNER", "Owner"),
                    ("EDITOR", "Editor"),
                    ("VIEWER", "Viewer"),
                ],
                default="EDITOR",
                max_length=200,
            ),
        ),
        migrations.AddField(
            model_name="instancepermission",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="instancepermission",
            name="team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="user_management.team",
            ),
        ),
        migrations.AddConstraint(
            model_name="instancepermission",
            constraint=models.UniqueConstraint(
                django.db.models.expressions.F("team"),
                django.db.models.expressions.F("instance"),
                condition=models.Q(("team__isnull", False)),
                name="instance_unique_team",
            ),
        ),
        migrations.AddConstraint(
            model_name="instancepermission",
            constraint=models.UniqueConstraint(
                django.db.models.expressions.F("user"),
                django.db.models.expressions.F("instance"),
                condition=models.Q(("user__isnull", False)),
                name="instance_unique_user",
            ),
        ),
        migrations.AddConstraint(
            model_name="instancepermission",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("team__isnull", False), ("user__isnull", False), _connector="OR"
                ),
                name="instance_permission_user_or_team_not_null",
            ),
        ),
    ]