# Generated by Django 3.2.6 on 2021-08-27 09:27

import uuid

import django.contrib.postgres.search
import django.db.models.deletion
import django_countries.fields
import django_ltree.fields
from django.db import migrations, models

import hexa.core.models.locale
import hexa.core.models.postgres


class Migration(migrations.Migration):
    dependencies = [
        ("tags", "0001_metadata_rf_4"),
        ("user_management", "0002_remove_username"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("catalog", "0010_metadata_rf_4"),
        ("core", "0007_ltree"),
    ]

    operations = [
        migrations.CreateModel(
            name="Index",
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
                ("object_id", models.UUIDField()),
                (
                    "path",
                    django_ltree.fields.PathField(blank=True, null=True, unique=True),
                ),
                ("label", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
                ("content", models.TextField(blank=True)),
                ("context", models.TextField(blank=True)),
                (
                    "countries",
                    django_countries.fields.CountryField(
                        blank=True, max_length=746, multiple=True
                    ),
                ),
                (
                    "locale",
                    hexa.core.models.locale.LocaleField(
                        choices=[
                            ("af", "Afrikaans"),
                            ("sq", "Albanian"),
                            ("ar-dz", "Algerian Arabic"),
                            ("ar", "Arabic"),
                            ("es-ar", "Argentinian Spanish"),
                            ("hy", "Armenian"),
                            ("ast", "Asturian"),
                            ("en-au", "Australian English"),
                            ("az", "Azerbaijani"),
                            ("eu", "Basque"),
                            ("be", "Belarusian"),
                            ("bn", "Bengali"),
                            ("bs", "Bosnian"),
                            ("pt-br", "Brazilian Portuguese"),
                            ("br", "Breton"),
                            ("en-gb", "British English"),
                            ("bg", "Bulgarian"),
                            ("my", "Burmese"),
                            ("ca", "Catalan"),
                            ("es-co", "Colombian Spanish"),
                            ("hr", "Croatian"),
                            ("cs", "Czech"),
                            ("da", "Danish"),
                            ("nl", "Dutch"),
                            ("en", "English"),
                            ("eo", "Esperanto"),
                            ("et", "Estonian"),
                            ("fi", "Finnish"),
                            ("fr", "French"),
                            ("fy", "Frisian"),
                            ("gl", "Galician"),
                            ("ka", "Georgian"),
                            ("de", "German"),
                            ("el", "Greek"),
                            ("he", "Hebrew"),
                            ("hi", "Hindi"),
                            ("hu", "Hungarian"),
                            ("is", "Icelandic"),
                            ("io", "Ido"),
                            ("ig", "Igbo"),
                            ("id", "Indonesian"),
                            ("ia", "Interlingua"),
                            ("ga", "Irish"),
                            ("it", "Italian"),
                            ("ja", "Japanese"),
                            ("kab", "Kabyle"),
                            ("kn", "Kannada"),
                            ("kk", "Kazakh"),
                            ("km", "Khmer"),
                            ("ko", "Korean"),
                            ("ky", "Kyrgyz"),
                            ("lv", "Latvian"),
                            ("lt", "Lithuanian"),
                            ("dsb", "Lower Sorbian"),
                            ("lb", "Luxembourgish"),
                            ("mk", "Macedonian"),
                            ("ml", "Malayalam"),
                            ("mr", "Marathi"),
                            ("es-mx", "Mexican Spanish"),
                            ("mn", "Mongolian"),
                            ("ne", "Nepali"),
                            ("es-ni", "Nicaraguan Spanish"),
                            ("no", "Norwegian"),
                            ("nb", "Norwegian Bokmal"),
                            ("nn", "Norwegian Nynorsk"),
                            ("os", "Ossetic"),
                            ("fa", "Persian"),
                            ("pl", "Polish"),
                            ("pt", "Portuguese"),
                            ("pa", "Punjabi"),
                            ("ro", "Romanian"),
                            ("ru", "Russian"),
                            ("gd", "Scottish Gaelic"),
                            ("sr", "Serbian"),
                            ("sr-latn", "Serbian Latin"),
                            ("zh-hans", "Simplified Chinese"),
                            ("sk", "Slovak"),
                            ("sl", "Slovenian"),
                            ("es", "Spanish"),
                            ("sw", "Swahili"),
                            ("sv", "Swedish"),
                            ("tg", "Tajik"),
                            ("ta", "Tamil"),
                            ("tt", "Tatar"),
                            ("te", "Telugu"),
                            ("th", "Thai"),
                            ("zh-hant", "Traditional Chinese"),
                            ("tr", "Turkish"),
                            ("tk", "Turkmen"),
                            ("udm", "Udmurt"),
                            ("uk", "Ukrainian"),
                            ("hsb", "Upper Sorbian"),
                            ("ur", "Urdu"),
                            ("uz", "Uzbek"),
                            ("es-ve", "Venezuelan Spanish"),
                            ("vi", "Vietnamese"),
                            ("cy", "Welsh"),
                        ],
                        default="en",
                        max_length=7,
                    ),
                ),
                ("last_synced_at", models.DateTimeField(blank=True, null=True)),
                ("external_id", models.TextField(blank=True)),
                ("external_type", models.TextField(blank=True)),
                ("external_subtype", models.TextField(blank=True)),
                ("external_name", models.TextField(blank=True)),
                ("external_description", models.TextField(blank=True)),
                (
                    "text_search_config",
                    hexa.core.models.postgres.PostgresTextSearchConfigField(
                        choices=[
                            ("simple", "simple"),
                            ("french", "french"),
                            ("english", "english"),
                        ],
                        default="simple",
                        max_length=100,
                    ),
                ),
                ("search", django.contrib.postgres.search.SearchVectorField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="user_management.organization",
                    ),
                ),
                ("tags", models.ManyToManyField(to="tags.Tag")),
            ],
            options={
                "verbose_name": "Catalog Index",
                "verbose_name_plural": "Catalog indexes",
                "ordering": ("external_name",),
            },
        ),
        migrations.CreateModel(
            name="IndexPermission",
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
                    "index",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="catalog.index"
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
        ),
        migrations.RemoveField(
            model_name="catalogindexpermission",
            name="catalog_index",
        ),
        migrations.RemoveField(
            model_name="catalogindexpermission",
            name="team",
        ),
        migrations.DeleteModel(
            name="CatalogIndex",
        ),
        migrations.DeleteModel(
            name="CatalogIndexPermission",
        ),
    ]
