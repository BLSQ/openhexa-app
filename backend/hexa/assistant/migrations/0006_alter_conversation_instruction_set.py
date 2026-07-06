from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assistant", "0005_message_content_segments"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="instruction_set",
            field=models.CharField(
                choices=[
                    ("general", "General"),
                    ("create_pipeline", "Create Pipeline"),
                    ("edit_pipeline", "Edit Pipeline"),
                    ("create_webapps", "Create Web Apps"),
                    ("edit_webapp", "Edit Web App"),
                ],
                default="general",
                max_length=50,
            ),
        ),
    ]
