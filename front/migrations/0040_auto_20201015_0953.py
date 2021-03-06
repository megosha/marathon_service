# Generated by Django 2.2.16 on 2020-10-15 06:53

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0039_auto_20201015_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
    ]
