from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("assistant", "0009_aiusage_backfill"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="conversation",
            name="asst_conv_user_cost_idx",
        ),
    ]
