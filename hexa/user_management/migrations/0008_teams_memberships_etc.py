# Generated by Django 4.0.2 on 2022-03-30 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0007_ci_email"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="membership",
            options={"ordering": ["team__name", "user__email"]},
        ),
        migrations.AlterModelOptions(
            name="team",
            options={"ordering": ["name"]},
        ),
        migrations.AddField(
            model_name="membership",
            name="role",
            field=models.CharField(
                choices=[("ADMIN", "Admin"), ("REGULAR", "Regular")],
                default="REGULAR",
                max_length=200,
            ),
        ),
    ]