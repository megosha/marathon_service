# Generated by Django 2.2.16 on 2020-09-30 11:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0033_auto_20200930_0630'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='mail_lesson_not_recieve',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='status_mail_lesson',
        ),
        migrations.AlterField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('d683de16-2daa-4a4b-bcd8-a6c36877ee2a'), primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
    ]
