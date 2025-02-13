# Generated by Django 2.2.16 on 2020-11-13 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0052_auto_20201105_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='uppersetting',
            name='mount_command',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Команда для монтирования удаленного хранилища видео'),
        ),
        migrations.AddField(
            model_name='uppersetting',
            name='remote_video_dir',
            field=models.FilePathField(blank=True, null=True, path='media/marathon/marathon/', verbose_name='Путь к папке с видеофайлами'),
        ),
        migrations.AddField(
            model_name='uppersetting',
            name='video_outer_url',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Префикс внешней ссылки на видеофайлы'),
        ),
        migrations.AlterField(
            model_name='account',
            name='looked_videos',
            field=models.ManyToManyField(blank=True, to='front.Video', verbose_name='Просмотренные видео'),
        ),
    ]
