# Generated by Django 2.2.16 on 2020-10-14 05:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0037_auto_20201013_0759'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='accepted',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Отзыв опубликован'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('df8035cc-4a63-417b-9f09-fcdb03c39445'), primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
    ]