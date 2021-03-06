# Generated by Django 2.2.16 on 2020-09-03 07:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=18, verbose_name='Контактный телефон')),
                ('photo', models.FileField(blank=True, upload_to='images/avatars/', verbose_name='Аватар')),
                ('feedback', models.TextField(blank=True, null=True, verbose_name='Отзыв')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Город')),
                ('date_registry', models.DateTimeField(auto_now=True, verbose_name='Дата публикации новости')),
                ('description', models.TextField(blank=True, default=None, null=True, verbose_name='Комментарий')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
