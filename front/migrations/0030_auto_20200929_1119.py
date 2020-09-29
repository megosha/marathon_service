# Generated by Django 2.2.16 on 2020-09-29 08:19

from django.db import migrations, models
import front.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0029_auto_20200928_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='hometask',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Домашнее задание по теме/вебинару'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='hometask_file',
            field=models.FileField(blank=True, null=True, upload_to=front.models.user_directory_path, verbose_name='Аватар'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('4c37b696-f5a1-44d8-a610-c40fd02c4300'), primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
    ]
