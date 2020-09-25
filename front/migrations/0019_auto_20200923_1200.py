# Generated by Django 2.2.16 on 2020-09-23 09:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0018_auto_20200923_0907'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='setting',
            name='soc_fb',
        ),
        migrations.RemoveField(
            model_name='setting',
            name='soc_vk',
        ),
        migrations.AddField(
            model_name='setting',
            name='soc_tm',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка на Telegram'),
        ),
        migrations.AddField(
            model_name='setting',
            name='soc_wa',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка на WhatsApp'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('e4f3fe2d-80bc-4df2-882f-038fc0cc6ca9'), primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
    ]
