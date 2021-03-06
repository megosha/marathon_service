# Generated by Django 2.2.16 on 2020-09-24 09:45

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0024_auto_20200924_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('8bdd1f80-04a8-4944-8da4-1ca335327889'), primary_key=True, serialize=False, verbose_name='Идентификатор платежа в системе / Ключ идемпотентности'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='main_marathon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='front.Marathon', verbose_name='Марафон на главной'),
        ),
    ]
