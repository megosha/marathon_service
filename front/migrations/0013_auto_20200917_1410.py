# Generated by Django 2.2.16 on 2020-09-17 11:10

import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0012_auto_20200917_1211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='id',
        ),
        migrations.AddField(
            model_name='payment',
            name='confirmation_token',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Идентификатор платежа в ЯК'),
        ),
        migrations.AddField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('de620505-fd33-4428-9ae3-7bbc2d1f2a71'), primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='date_publish',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 9, 17, 14, 10, 41, 526541), null=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='video',
            name='date_publish',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 9, 17, 14, 10, 41, 527973), null=True, verbose_name='Дата публикации'),
        ),
    ]