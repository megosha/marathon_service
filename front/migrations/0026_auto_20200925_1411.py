# Generated by Django 2.2.16 on 2020-09-25 11:11

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0025_auto_20200924_1245'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='invoice_email',
            field=models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Email для квитанции'),
        ),
        migrations.AddField(
            model_name='setting',
            name='invoice_fio',
            field=models.CharField(blank=True, default='Торопчин Артём Викторович', max_length=100, null=True, verbose_name='ФИО для квитанции'),
        ),
        migrations.AddField(
            model_name='setting',
            name='invoice_phone',
            field=models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Телефон для квитанции'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('cd7604bd-8290-4fb9-91a2-911e26b49aed'), primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
    ]
