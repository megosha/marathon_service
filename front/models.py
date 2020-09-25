import uuid
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.utils.safestring import mark_safe

from os import path
from front.make_invoice import create_pdf


# Create your models here.


class UpperSetting(models.Model):
    endpoint = models.CharField(max_length=250, blank=True, null=True, verbose_name="Адрес API к сервису")
    metadescr = models.TextField(default='', blank=True, null=True, verbose_name="Meta Description")
    metakeywords = models.TextField(default='', blank=True, null=True, verbose_name="Meta Keyword")
    shopid = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID магазина в ЯК")
    yandex_api_key = models.CharField(max_length=250, blank=True, null=True, verbose_name="yandex_api_key")
    shopid_test = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID тестового магазина в ЯК")
    yandex_api_key_test = models.CharField(max_length=250, blank=True, null=True, verbose_name="yandex_api_key_test")
    test_mode = models.BooleanField(default=False, verbose_name="Тестовый режим ЯК")
    return_url = models.CharField(max_length=250, blank=True, null=True, verbose_name="return_url для ЯК")


class Marathon(models.Model):
    title = models.CharField(max_length=250, blank=False, null=False, verbose_name="Название темы/вебинара")
    cost = models.PositiveIntegerField(default=0, verbose_name="Стоимость марафона (в рублях)")
    date_start = models.DateTimeField(default=None, blank=True, null=True, verbose_name="Дата старта марафона")
    date_create = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="Дата создания")
    promo = models.CharField(max_length=100, null=True, blank=True, verbose_name="Ссылка на YouTube-видео (Промо-ролик)")
    description = models.TextField(verbose_name="Комментарий/Описание", default=None, blank=True, null=True)

    class Meta:
        verbose_name = "Марафон"
        verbose_name_plural = "Марафоны"

    def __str__(self):
        return f"{self.title}"


class Setting(models.Model):
    website = models.URLField(blank=True, null=True, verbose_name="Адрес сайта")
    contact_phone = models.CharField(max_length=18, blank=True, null=True, verbose_name="Контактный телефон")
    contact_mail = models.EmailField(blank=True, null=True, verbose_name="Контактный Email")
    soc_igm = models.URLField(blank=True, null=True, verbose_name="Ссылка на Instagram")
    soc_tm = models.URLField(blank=True, null=True, verbose_name="Ссылка на Telegram")
    soc_wa = models.URLField(blank=True, null=True, verbose_name="Ссылка на WhatsApp")
    fake_cost = models.PositiveIntegerField(default=2500, verbose_name="Стоимость марафона (в рублях) до скидки")
    main_marathon = models.ForeignKey(Marathon, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name="Марафон на главной")
    invoice_fio = models.CharField(max_length=100, default="Торопчин Артём Викторович", blank=True, null=True, verbose_name="ФИО для квитанции")
    invoice_phone = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name="Телефон для квитанции")
    invoice_email = models.CharField(max_length=50, default="", blank=True, null=True, verbose_name="Email для квитанции")


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


class ReviewKind(models.Model):
    kind = models.CharField(max_length=250, blank=True, null=True, verbose_name="Тип отзыва")

    class Meta:
        verbose_name = "Категория отзывов"
        verbose_name_plural = "Категории отзывов"

    def __str__(self):
        return f"{self.kind}"


class Feedback(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Аккаунт на сайте")
    kind = models.ForeignKey(ReviewKind, default=None, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Тип отзыва")
    feedback = models.TextField(null=True, blank=True, verbose_name="Отзыв")
    date_create = models.DateTimeField(auto_now=True, verbose_name="Дата создания отзыва")
    custom_user = models.CharField(max_length=250, blank=True, null=True, verbose_name="Имя (ручное добавление)")
    custom_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    custom_photo = models.FileField(upload_to='images/avatars/', blank=True, verbose_name="Аватар")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.account} / {self.custom_user}"


class Lesson(models.Model):
    marathon = models.ForeignKey(Marathon, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Марафон")
    number = models.PositiveSmallIntegerField(null=False, blank=False,
                                      verbose_name="Порядковый номер темы в марафоне")
    title = models.CharField(max_length=250, blank=False, null=False, verbose_name="Название темы/вебинара")
    free = models.BooleanField(default=False, verbose_name="Тема доступна без покупки марафона")
    description = models.TextField(default=None, blank=True, null=True, verbose_name="Комментарий к теме/вебинару")
    # cost = models.PositiveIntegerField(default=0, verbose_name="Стоимость темы (в рублях)")
    date_create = models.DateTimeField(auto_now=True, verbose_name="Дата создания")
    date_publish = models.DateTimeField(default=timezone.now, blank=True, null=True, verbose_name="Дата публикации")

    class Meta:
        unique_together = ('number', 'marathon')
        verbose_name = "Тема/Вебинар"
        verbose_name_plural = "Темы/Вебинары"

    def __str__(self):
        return f"Тема:{self.title} -  №{self.number} - марафон: {self.marathon}"


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Тема/Вебинар")
    number = models.PositiveSmallIntegerField(null=False, blank=False,
                                      verbose_name="Порядковый номер видео (номер отображения в уроке)")
    link = models.CharField(max_length=25, null=True, blank=True, verbose_name="ID видео на YouTube")
    description = models.TextField(default=None, blank=True, null=True, verbose_name="Комментарий к видео")
    date_create = models.DateTimeField(auto_now=True, verbose_name="Дата создания")
    # date_publish = models.DateTimeField(default=timezone.now, blank=True, null=True, verbose_name="Дата публикации")
    # video = models.FileField(null=True, blank=True, verbose_name="Видеофйал")

    class Meta:
        unique_together = ('number', 'lesson')
        verbose_name = "Видео"
        verbose_name_plural = "Видео"

    def __str__(self):
        return f"{self.lesson.title} -  №{self.number}"


class Payment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4(), blank=True, primary_key=True, verbose_name="Идентификатор платежа в системе / Ключ идемпотентности")
    amount = models.PositiveIntegerField(default=0, verbose_name="Сумма платежа")
    account = models.ForeignKey(Account, blank=False, null=False, on_delete=models.DO_NOTHING, verbose_name="Аккаунт")
    # lesson = models.ForeignKey(Lesson, blank=False, null=False, on_delete=models.DO_NOTHING, verbose_name="Тема/Вебинар")
    marathon = models.ForeignKey(Marathon, default=None, blank=False, null=False, on_delete=models.DO_NOTHING, verbose_name="Марафон")
    date_pay = models.DateTimeField(auto_now=True, blank=False, null=False, verbose_name="Дата оплаты")
    date_approve = models.DateTimeField(blank=True, null=True, verbose_name="Дата подтверждения платежа")
    request = models.TextField(blank=True, null=True, verbose_name="Запрос в ЯК")
    response = models.TextField(blank=True, null=True, verbose_name="Ответ от ЯК")
    yuid = models.CharField(max_length=250, blank=True, null=True, verbose_name="Идентификатор платежа в ЯК")
    confirmation_token = models.CharField(max_length=250, blank=True, null=True, verbose_name="confirmation_token")
    invoice = models.CharField(max_length=250, blank=True, null=True, verbose_name="Квитанция")
    status = models.CharField(max_length=250, blank=True, null=True, verbose_name="Статус платежа в ЯК")
    # status_mail_invoice = models.BooleanField(default=None, blank=True, null=True, verbose_name="Квитанция отправлена отправлена")
    status_mail_lesson = models.BooleanField(default=None, blank=True, null=True, verbose_name="Напоминание в день урока отправлено")

    class Meta:
        # unique_together = ('account', 'lesson') - #TODO по истечении двух месяцев повторный платеж
        verbose_name = "Платёж"
        verbose_name_plural = "Платёжи"

    def __str__(self):
        return f"account.pk: {self.account.pk} -  №{self.pk}"

    def save(self, *args, **kwargs):
        if not self.invoice and self.status == 'succeeded':
            self.invoice = create_pdf(self)
        super(Payment, self).save(*args, **kwargs)

    def icon_tag(self):
        if not (self.uuid and self.invoice):
            return ''
        return mark_safe(f'<a href="{path.join(settings.MEDIA_URL, "invoice", self.uuid.__str__())}.pdf" target="_blank">Квитанция {self.uuid}</a>')


class Logging():
    date = models.DateTimeField(auto_now=True, blank=False, null=False, verbose_name="Дата действия")
    action = models.TextField(blank=True, null=True, verbose_name="Действие")
    input_data = models.TextField(blank=True, null=True, verbose_name="Данные на входе")
    output_data = models.TextField(blank=True, null=True, verbose_name="Данные на выходе")
