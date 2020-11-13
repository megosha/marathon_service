# Generated by Django 2.2.16 on 2020-11-05 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0051_auto_20201028_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='looked_videos',
            field=models.ManyToManyField(blank=True, to='front.Video'),
        ),
        migrations.AddField(
            model_name='video',
            name='url',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Ссылка для просмотра видео'),
        ),
    ]