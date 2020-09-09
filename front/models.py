import uuid
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


# Create your models here.
class UpperSetting(models.Model):
    endpoint = models.CharField(max_length=250, blank=True, null=True, verbose_name="Адрес API к сервису")
    metadescr = models.TextField(default='', blank=True, null=True, verbose_name="Meta Description")
    metakeywords = models.TextField(default='', blank=True, null=True, verbose_name="Meta Keyword")

class Setting(models.Model):
    website = models.URLField(blank=True, null=True, verbose_name="Адрес сайта")
    contact_phone = models.CharField(max_length=18, blank=True, null=True, verbose_name="Контактный телефон")
    contact_mail = models.EmailField(blank=True, null=True, verbose_name="Контактный Email")
    soc_igm = models.URLField(blank=True, null=True, verbose_name="Ссылка на Instagram")
    soc_vk = models.URLField(blank=True, null=True, verbose_name="Ссылка на Вконтакте")
    soc_fb = models.URLField(blank=True, null=True, verbose_name="Ссылка на Facebook")



class Marathon(models.Model):
    title = models.CharField(max_length=250, blank=False, null=False, verbose_name="Название темы/вебинара")
    date_start = models.DateTimeField(default=None, blank=True, null=True, verbose_name="Дата старта марафона")
    date_create = models.DateTimeField(default=None, blank=True, null=True, verbose_name="Дата создания")
    description = models.TextField(verbose_name="Комментарий/Описание", default=None, blank=True, null=True)

    class Meta:
        verbose_name = "Марафон"
        verbose_name_plural = "Марафоны"

    def __str__(self):
        return f"{self.title}"


class Account(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=18, blank=False, null=False, verbose_name="Контактный телефон")
    approved = models.BooleanField(default=False, blank=True, null=True,
                                        verbose_name="Статус подтверждения аккаунта (совершен вход в ЛК)")
    registry_sent = models.BooleanField(default=None, blank=True, null=True,
                                        verbose_name="Письмо о регистрации отправлено")
    date_registry = models.DateTimeField(auto_now=True, verbose_name="Дата регистрации")
    description = models.TextField(verbose_name="Комментарий", default=None, blank=True, null=True)
    photo = models.FileField(upload_to='images/avatars/', blank=True, verbose_name="Аватар")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    marathone = models.ManyToManyField('Marathon', blank=True, verbose_name="Марафоны")

    class Meta:
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"

    def __str__(self):
        return f"{self.user.get_full_name()}"


class Feedback(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Отзыв")
    feedback = models.TextField(null=True, blank=True, verbose_name="Отзыв")
    date_create = models.DateTimeField(auto_now=True, verbose_name="Дата создания отзыва")
    custom_user = models.CharField(max_length=250, blank=True, null=True, verbose_name="Имя")
    custom_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    custom_photo = models.FileField(upload_to='images/avatars/', blank=True, verbose_name="Аватар")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.account} / {self.custom_user}"


class Lesson(models.Model):
    marathon = models.ForeignKey(Marathon, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Марафон")
    number = models.SmallIntegerField(null=False, blank=False,
                                      verbose_name="Порядковый номер темы в марафоне")
    title = models.CharField(max_length=250, blank=False, null=False, verbose_name="Название темы/вебинара")
    description = models.TextField(default=None, blank=True, null=True, verbose_name="Комментарий к теме/вебинару")
    cost = models.DecimalField(default=0, decimal_places=2, max_digits=20, blank=True,
                                   verbose_name="Стоимость темы (в рублях)")
    date_create = models.DateTimeField(auto_now=True, verbose_name="Дата создания")
    date_publish = models.DateTimeField(default=datetime.now(), blank=True, null=True, verbose_name="Дата публикации")

    class Meta:
        unique_together = ('number', 'marathon')
        verbose_name = "Тема/Вебинар"
        verbose_name_plural = "Темы/Вебинары"

    def __str__(self):
        return f"Тема:{self.title} -  №{self.number} - марафон: {self.marathon}"


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Тема/Вебинар")
    number = models.SmallIntegerField(null=False, blank=False,
                                      verbose_name="Порядковый номер видео (номер отображения в уроке)")
    link = models.TextField(null=True, blank=True, verbose_name="Ссылка на YouTube видео")
    description = models.TextField(default=None, blank=True, null=True, verbose_name="Комментарий к видео")
    date_create = models.DateTimeField(auto_now=True, verbose_name="Дата создания")
    date_publish = models.DateTimeField(default=datetime.now(), blank=True, null=True, verbose_name="Дата публикации")
    # video = models.FileField(null=True, blank=True, verbose_name="Видеофйал")

    class Meta:
        unique_together = ('number', 'lesson')
        verbose_name = "Видео"
        verbose_name_plural = "Видео"

    def __str__(self):
        return f"{self.lesson.title} -  №{self.number}"


# class Payment(models.Model):
#     date_pay = models.DateTimeField(auto_now=True, blank=False, null=False, verbose_name="Дата оплаты")
#
#
# class Logging():
#     pass
