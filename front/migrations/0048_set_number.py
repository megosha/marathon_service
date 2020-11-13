# Generated by Django 2.2.16 on 2020-10-27 10:02

from django.db import migrations

def set_number(apps, schema_editor):
    GiftItems = apps.get_model('front', 'GiftItems')
    for i, item in enumerate(GiftItems.objects.all()):
        item.number = i
        item.save()



class Migration(migrations.Migration):

    dependencies = [
        ('front', '0047_auto_20201027_1258'),
    ]

    operations = [
        migrations.RunPython(set_number),
    ]