# Generated by Django 2.2.16 on 2020-12-03 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0055_auto_20201120_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gift',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='files/gifts/', verbose_name='Файл подарка (книга)'),
        ),
        migrations.AlterField(
            model_name='marathon',
            name='subtitle',
            field=models.CharField(blank=True, default='', max_length=250, null=True, verbose_name='Подзаголовок (на Главной)'),
        ),
    ]