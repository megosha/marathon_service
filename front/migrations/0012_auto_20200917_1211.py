# Generated by Django 2.2.16 on 2020-09-17 09:11

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0011_auto_20200916_0911'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reviewkind',
            options={'verbose_name': 'Категория отзывов', 'verbose_name_plural': 'Категории отзывов'},
        ),
        migrations.AlterField(
            model_name='feedback',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='front.Account', verbose_name='Аккаунт на сайте'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='custom_user',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Имя (ручное добавление)'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='cost',
            field=models.PositiveIntegerField(default=0, verbose_name='Стоимость темы (в рублях)'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='date_publish',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 9, 17, 12, 11, 29, 160804), null=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='video',
            name='date_publish',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 9, 17, 12, 11, 29, 161346), null=True, verbose_name='Дата публикации'),
        ),
    ]
