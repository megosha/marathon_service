# Generated by Django 2.2.16 on 2020-09-24 09:45

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0023_auto_20200924_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='main_marathon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='front.Marathon', verbose_name='Марафон'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('764a14ab-87c5-454b-8790-181237794478'), primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='fake_cost',
            field=models.PositiveIntegerField(default=2500, verbose_name='Стоимость марафона (в рублях) до скидки'),
        ),
    ]
