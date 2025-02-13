# Generated by Django 2.2.16 on 2020-09-22 09:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0016_auto_20200922_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Квитанция'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('bcddac27-b775-46ba-acaa-cf5a47f37f7b'), primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
    ]
