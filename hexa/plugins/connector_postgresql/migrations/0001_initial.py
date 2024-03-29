# Generated by Django 3.2.5 on 2021-08-03 16:40

import uuid

import django.db.models.deletion
from django.db import migrations, models

import hexa.core.models.cryptography


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("user_management", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostgresqlDatabase",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("hostname", models.CharField(max_length=200)),
                ("username", models.CharField(max_length=200)),
                (
                    "password",
                    hexa.core.models.cryptography.EncryptedTextField(max_length=200),
                ),
                ("port", models.IntegerField(default=5432)),
                ("database", models.CharField(max_length=200)),
                ("postfix", models.CharField(blank=True, max_length=200)),
            ],
            options={
                "verbose_name": "Postgresql Database",
                "ordering": ("hostname",),
                "unique_together": {("database", "postfix")},
            },
        ),
        migrations.CreateModel(
            name="PostgresqlDatabasePermission",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "database",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="connector_postgresql.postgresqldatabase",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="user_management.team",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
