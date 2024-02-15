from django.db import migrations


def cleanse_objects(apps, schema_editor):
    # at some point, we got duplicates in the DB. this code clean up the mess.
    # we don't known which object is "legit" and which is a dup -> keep the first one, remove the others
    Bucket = apps.get_model("connector_s3", "Bucket")
    for bucket in Bucket.objects.all():
        seen = set()
        for object in bucket.object_set.all():
            if object.key in seen:
                object.delete()
            else:
                seen.add(object.key)


class Migration(migrations.Migration):
    dependencies = [
        ("connector_s3", "0026_remove_object_orphan"),
    ]

    operations = [
        migrations.RunPython(cleanse_objects, lambda *a, **b: None),
    ]
