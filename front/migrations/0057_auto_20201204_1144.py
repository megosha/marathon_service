# Generated by Django 2.2.16 on 2020-12-04 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0056_auto_20201203_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='instruction',
            field=models.FileField(blank=True, null=True, upload_to='files/', verbose_name='Документация на сайт'),
        ),
    ]
