# Generated by Django 2.2.16 on 2020-12-10 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0058_video_url_empty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='url',
            field=models.TextField(blank=True, default='', verbose_name='Ссылка для просмотра видео'),
        ),
    ]
