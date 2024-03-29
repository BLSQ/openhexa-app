# Generated by Django 3.2.6 on 2021-09-14 14:02

import uuid

import django.contrib.postgres.indexes
import django.db.models.deletion
import django_countries.fields
from django.db import migrations, models

import hexa.core.models.locale
import hexa.core.models.path
import hexa.core.models.postgres


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("user_management", "0003_feature_flags"),
        ("tags", "0001_metadata_rf_4"),
        ("pipelines", "0005_longer_text_fields"),
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
                ("path", hexa.core.models.path.PathField(blank=True, null=True)),
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
                ("search", models.TextField(blank=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="user_management.organization",
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        blank=True,
                        related_name="_pipelines_index_tags_+",
                        to="tags.Tag",
                    ),
                ),
            ],
            options={
                "verbose_name": "Pipeline index",
                "verbose_name_plural": "Pipeline indexes",
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
                ("permission_id", models.UUIDField(null=True)),
                (
                    "index",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pipelines.index",
                    ),
                ),
                (
                    "permission_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="user_management.team",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.RemoveField(
            model_name="pipelinesindexpermission",
            name="pipeline_index",
        ),
        migrations.RemoveField(
            model_name="pipelinesindexpermission",
            name="team",
        ),
        migrations.DeleteModel(
            name="PipelinesIndex",
        ),
        migrations.DeleteModel(
            name="PipelinesIndexPermission",
        ),
        migrations.AddIndex(
            model_name="index",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search"],
                name="pipeline_index_search_gin_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="index",
            index=django.contrib.postgres.indexes.GistIndex(
                fields=["search"],
                name="pipeline_index_search_gist_idx",
                opclasses=["gist_trgm_ops"],
            ),
        ),
    ]
