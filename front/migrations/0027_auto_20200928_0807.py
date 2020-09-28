# Generated by Django 2.2.16 on 2020-09-28 05:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0026_auto_20200925_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='status_mail_invoice',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='Квитанция отправлена'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('3255e9f2-ff21-46d9-9989-5e545d776ced'), primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
    ]
