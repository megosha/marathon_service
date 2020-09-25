# Generated by Django 2.2.16 on 2020-09-08 08:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0003_auto_20200908_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='UpperSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.CharField(blank=True, max_length=250, null=True, verbose_name='Адрес API к сервису')),
                ('metadescr', models.TextField(blank=True, default='', null=True, verbose_name='Meta Description')),
                ('metakeywords', models.TextField(blank=True, default='', null=True, verbose_name='Meta Keyword')),
            ],
        ),
        migrations.AlterModelOptions(
            name='marathon',
            options={'verbose_name': 'Марафон', 'verbose_name_plural': 'Марафоны'},
        ),
        migrations.RemoveField(
            model_name='setting',
            name='metadescr',
        ),
        migrations.RemoveField(
            model_name='setting',
            name='metakeywords',
        ),
        migrations.AlterField(
            model_name='lesson',
            name='date_publish',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 9, 8, 15, 0, 20, 121648), null=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='video',
            name='date_publish',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 9, 8, 15, 0, 20, 122256), null=True, verbose_name='Дата публикации'),
        ),
    ]
