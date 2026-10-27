from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("assistant", "0007_alter_conversation_instruction_set"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="conversation",
            name="asst_conv_user_cost_idx",
        ),
    ]
