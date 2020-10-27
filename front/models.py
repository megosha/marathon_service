import uuid
from datetime import timedelta
from os import path
import environ

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe

from front.make_invoice import create_pdf


# Create your models here.

base_dir = settings.BASE_DIR
# medis_dir = settings.MEDIA_ROOT

env = environ.Env()
env.read_env(path.join(base_dir, '.env'))

# statuses = {'pending': 'Платёж создан (в обработке)',
#             'waiting_for_capture': 'Платёж оплачен, деньги авторизованы и ожидают списания',
#             'succeeded': 'Платёж успешно завершён',
#              'canceled': 'Платёж отменён'}
statuses = ((1, 'pending'),
            (2, 'waiting_for_capture'),
            (3, 'canceled'),
            (4, 'succeeded'),
            )


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<marathon.name>/<lesson.number.*>
    try:
        return f'hometasks/{instance.marathon.pk}/{instance.number}.{filename[filename.rfind(".") + 1:]}'
    except:
        return f'hometasks/{instance.marathon.pk}/{filename}'

def video_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<marathon.name>/<lesson.number.*>
    try:
        return f'video/{instance.lesson.marathon.pk}/{instance.lesson.number}_{instance.number}.{filename[filename.rfind(".") + 1:]}'
    except:
        return f'hometasks/{instance.lesson.marathon.pk}/{filename}'

def sendmail(subject, message, recipient_list, from_email=None, attach: iter = None):
    if from_email is None:
        from_email = env('FROM_EMAIL')
    if type(recipient_list) == str:
        recipient_list = [recipient_list]
    if type(attach) == str:
        attach = [attach]
    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list)
    mail.content_subtype = "html"
    if attach:
        for file in attach:
            if isinstance(file, str):
                try:
                    mail.attach_file(path.join(settings.MEDIA_ROOT, 'invoice', file))
                except Exception as e:
                    print(e)
                    pass
    log = Logging.objects.create(action="Отправка письма",
                                 input_data=f"{subject}\n{from_email}\n{recipient_list}")
    try:
        mail.send(fail_silently=False)
    except Exception as ex:
        log.result = log.FAIL
        log.output_data = f"{ex}"
        log.save()
        print(ex)
        return False
    else:
        log.result = log.SUCCESS
        log.save()
        return True


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
    title = models.CharField(max_length=250, blank=False, null=False, verbose_name="Название марафона (на Главной)")
    subtitle = models.CharField(max_length=250, blank=False, null=False, default="", verbose_name="Подзаголовок (на Главной)")
    advantages = models.TextField(verbose_name="Достоинства (на Главной)", default="", blank=True, null=True)
    cost = models.PositiveIntegerField(default=0, verbose_name="Стоимость марафона (в рублях)")
    date_start = models.DateTimeField(default=None, blank=True, null=True, verbose_name="Дата старта марафона")
    date_create = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="Дата создания")
    promo = models.CharField(max_length=100, null=True, blank=True,
                             verbose_name="Ссылка на YouTube-видео (Промо-ролик на Главной)")
    description = models.TextField(verbose_name="Комментарий/Описание", default=None, blank=True, null=True)
    outdated = models.BooleanField(default=False, verbose_name="Скрыть марафон с сайта")

    class Meta:
        verbose_name = "Марафон"
        verbose_name_plural = "Марафоны"

    def title_general(self):
        return str(self.title).upper()[:str(self.title).rfind(' ')]

    def title_last(self):
        return str(self.title).upper()[str(self.title).rfind(' ') + 1:]

    def subtitle_upper(self):
        return str(self.subtitle).upper()

    def ad_list(self):
        return self.advantages.strip().split("\n")
        # return self.advantages.split("\n")

    def __str__(self):
        return f"{self.title}"


class Gift(models.Model):
    marathon = models.OneToOneField(Marathon, on_delete=models.CASCADE, verbose_name="Марафон")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    photo = models.ImageField(upload_to='images/gifts/', blank=True, verbose_name="Картинка на сайте")

    class Meta:
        verbose_name = "Подарки и Бонусы марафонов"
        verbose_name_plural = "Подарки и Бонусы марафонов"

    def __str__(self):
        return f"{self.marathon.title}"


class GiftItems(models.Model):
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, verbose_name="Бонус марафона")
    icon = models.CharField(max_length=35, blank=True, null=True, verbose_name="Иконка fa-awesome")
    advantage = models.CharField(max_length=255, verbose_name="Подпункт")
    number = models.PositiveSmallIntegerField(null=False, blank=False,
                                              verbose_name="Порядковый номер отображения на сайте")

    class Meta:
        ordering = ["number"]
        unique_together = ('number', 'gift')
        verbose_name = "Подпункты Подарков и Бонусов марафонов"
        verbose_name_plural = "Подпункты Подарков и Бонусов марафонов"

    def __str__(self):
        return f"{self.gift}"


class Setting(models.Model):
    website = models.URLField(blank=True, null=True, verbose_name="Адрес сайта")
    contact_phone = models.CharField(max_length=18, blank=True, null=True, verbose_name="Контактный телефон")
    contact_mail = models.EmailField(blank=True, null=True, verbose_name="Контактный Email")
    soc_igm = models.URLField(blank=True, null=True, verbose_name="Ссылка на Instagram")
    soc_tm = models.URLField(blank=True, null=True, verbose_name="Ссылка на Telegram")
    soc_wa = models.URLField(blank=True, null=True, verbose_name="Ссылка на WhatsApp")
    fake_cost = models.PositiveIntegerField(default=2500, verbose_name="Стоимость марафона (в рублях) до скидки")
    main_marathon = models.ForeignKey(Marathon, blank=True, null=True, on_delete=models.DO_NOTHING,
                                      verbose_name="Марафон на главной")
    invoice_fio = models.CharField(max_length=100, default="Торопчин Артём Викторович", blank=True, null=True,
                                   verbose_name="ФИО для квитанции")
    invoice_phone = models.CharField(max_length=50, default="", blank=True, null=True,
                                     verbose_name="Телефон для квитанции")
    invoice_email = models.CharField(max_length=50, default="", blank=True, null=True,
                                     verbose_name="Email для квитанции")
    instruction = models.FileField("Руководство администратора", blank=True, null=True)


class Account(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=18, blank=False, null=False, verbose_name="Контактный телефон")
    approved = models.BooleanField(default=False, blank=True, null=True,
                                   verbose_name="Статус подтверждения аккаунта (совершен вход в ЛК)")
    registry_sent = models.BooleanField(default=None, blank=True, null=True,
                                        verbose_name="Письмо о регистрации отправлено")
    date_registry = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    description = models.TextField(verbose_name="Комментарий", default=None, blank=True, null=True)
    photo = models.ImageField(upload_to='images/avatars/', blank=True, verbose_name="Аватар")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")

    class Meta:
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"

    def __str__(self):
        return f"{self.user.get_full_name()}"

    def has_success_payment(self):
        return self.payment_set.filter(status="succeeded").exists()


class Mailing(models.Model):
    PAYED = 1
    NOT_PAYED = 2
    ALL = 3
    RECIPIENTS = (
        (PAYED, "Оплатившие"),
        (NOT_PAYED, "Не оплатившие"),
        (ALL, "Все")
    )
    date = models.DateTimeField("Дата рассылки")
    recipient = models.SmallIntegerField("Получатели", choices=RECIPIENTS, default=ALL)
    marathon = models.ForeignKey(Marathon, verbose_name="Марафон", on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField("Тема письма", max_length=250, default="")
    message = models.TextField("Сообщение", default="")
    attach = models.FileField("Вложение", blank=True)
    active = models.BooleanField("Активна", default=False, blank=True)

    class Meta:
        app_label = 'front'
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def save(self, *args, **kwargs):
        super(Mailing, self).save(*args, **kwargs)
        if self.active:
            from front.tasks import start_mailing
            if self.date <= timezone.now():
                self.date = timezone.now() + timedelta(seconds=10)
            start_mailing.apply_async([self.pk], eta=self.date)


class ReviewKind(models.Model):
    kind = models.CharField(max_length=250, blank=True, null=True, verbose_name="Тип отзыва")

    class Meta:
        verbose_name = "Категория отзывов"
        verbose_name_plural = "Категории отзывов"

    def __str__(self):
        return f"{self.kind}"


class Feedback(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL,
                                verbose_name="Аккаунт на сайте")
    kind = models.ForeignKey(ReviewKind, default=1, blank=True, null=True, on_delete=models.SET_NULL,
                             verbose_name="Тип отзыва")
    feedback = models.TextField(null=True, blank=True, verbose_name="Отзыв")
    accepted = models.BooleanField(default=False, blank=True, null=True,
                                        verbose_name="Отзыв опубликован")
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания отзыва")
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
    description = models.TextField(default=None, blank=True, null=True, verbose_name="Подэтапы, описание, пункты темы через запятую")
    hometask = models.TextField(default=None, blank=True, null=True, verbose_name="Домашнее задание по теме/вебинару")
    hometask_file = models.FileField(upload_to=user_directory_path, null=True, blank=True,
                                     verbose_name="Файл Домашнего задания по теме/вебинару")
    # cost = models.PositiveIntegerField(default=0, verbose_name="Стоимость темы (в рублях)")
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    date_publish = models.DateTimeField(default=timezone.now, blank=True, null=True, verbose_name="Дата публикации")

    # status_mail_lesson = models.BooleanField(default=None, blank=True, null=True, verbose_name="Напоминание в день урока отправлено")
    # mail_lesson_not_recieve = models.TextField(default=None, blank=True, null=True, verbose_name="Напоминание не получили")

    class Meta:
        unique_together = ('number', 'marathon')
        verbose_name = "Тема/Вебинар"
        verbose_name_plural = "Темы/Вебинары"

    def description_as_list(self):
        # return self.description.split(',')
        return self.description.strip().split("\n")


    def __str__(self):
        return f"Тема:{self.title} -  №{self.number} - марафон: {self.marathon}"


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Тема/Вебинар")
    number = models.PositiveSmallIntegerField(null=False, blank=False,
                                              verbose_name="Порядковый номер видео (номер отображения в уроке)")
    video = models.FileField(upload_to=video_directory_path, default=None, null=True, blank=True, verbose_name="Видеофайл, .mp4")
    link = models.CharField(max_length=25, null=True, blank=True, verbose_name="ID видео на YouTube (устаревшее)")
    description = models.TextField(default=None, blank=True, null=True, verbose_name="Комментарий к видео")
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    # date_publish = models.DateTimeField(default=timezone.now, blank=True, null=True, verbose_name="Дата публикации")

    class Meta:
        ordering = ["number"]
        unique_together = ('number', 'lesson')
        verbose_name = "Видео"
        verbose_name_plural = "Видео"

    def __str__(self):
        return f"{self.lesson.title} -  №{self.number}"


class Payment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, blank=True, primary_key=True,
                            verbose_name="Идентификатор платежа в системе / Ключ идемпотентности")
    amount = models.PositiveIntegerField(default=0, verbose_name="Сумма платежа")
    account = models.ForeignKey(Account, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Аккаунт")
    # lesson = models.ForeignKey(Lesson, blank=False, null=False, on_delete=models.DO_NOTHING, verbose_name="Тема/Вебинар")
    marathon = models.ForeignKey(Marathon, default=None, blank=False, null=False, on_delete=models.DO_NOTHING,
                                 verbose_name="Марафон")
    date_pay = models.DateTimeField(auto_now_add=True, blank=False, null=False, verbose_name="Дата оплаты")
    date_approve = models.DateTimeField(blank=True, null=True, verbose_name="Дата подтверждения платежа")
    request = models.TextField(blank=True, null=True, verbose_name="Запрос в ЯК")
    response = models.TextField(blank=True, null=True, verbose_name="Ответ от ЯК")
    yuid = models.CharField(max_length=250, blank=True, null=True, verbose_name="Идентификатор платежа в ЯК")
    confirmation_token = models.CharField(max_length=250, blank=True, null=True, verbose_name="confirmation_token")
    invoice = models.CharField(max_length=250, blank=True, null=True, verbose_name="Квитанция")
    status = models.CharField(max_length=250, blank=True, null=True, verbose_name="Статус платежа в ЯК")
    status_mail_invoice = models.BooleanField(default=None, blank=True, null=True, verbose_name="Квитанция отправлена")

    # status_mail_lesson = models.BooleanField(default=None, blank=True, null=True, verbose_name="Напоминание в день урока отправлено")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"№{self.pk}"

    def save(self, *args, **kwargs):
        if self.status == 'succeeded':
            if not self.invoice:
                self.invoice = create_pdf(self)
                self.send_invoice()
        super(Payment, self).save(*args, **kwargs)

    def send_invoice(self):
        sett = Setting.objects.filter().first()
        mail_context = {"settings": sett, 'payment': self}
        html_message = render_to_string('mail/invoice.html', mail_context)
        send_email = sendmail(subject=f'Оплата подписки на марафон "{self.marathon.title}"',
                              recipient_list=[self.account.user.email],
                              message=html_message, attach=f'{self.uuid}.pdf')
        self.status_mail_invoice = send_email

    def status_set(self, new_status):
        Payment.objects.filter(pk=self.pk).update(status=new_status)
        if new_status == 'succeeded':
            self.date_approve = timezone.now()
        elif new_status == 'canceled' and self.status == 'succeeded':
            sett = Setting.objects.filter().first()
            message = "<p>Ваш платёж был отменен.</p>"
            mail_context = {"settings": sett, 'message': message}
            html_message = render_to_string('mail/new_lesson_notify.html', mail_context)
            send_email = sendmail(subject=f'Оплата подписки на марафон "{self.marathon.title}"',
                                  recipient_list=[self.account.user.email],
                                  message=html_message, attach=f'{self.uuid}.pdf')

        self.status = new_status
        self.save()

    def icon_tag(self):
        if not (self.uuid and self.invoice):
            return ''
        return mark_safe(
            f'<a href="{path.join(settings.MEDIA_URL, "invoice", self.uuid.__str__())}.pdf" target="_blank">Квитанция {self.uuid}</a>')


class Logging(models.Model):
    CREATED = 0
    SUCCESS = 1
    FAIL = 2
    RESULT = (
        (CREATED, "Создано"),
        (SUCCESS, "Успешно"),
        (FAIL, "Ошибка"),
    )
    date = models.DateTimeField(auto_now_add=True, blank=False, null=False, verbose_name="Дата действия")
    action = models.TextField(blank=True, null=True, verbose_name="Действие")
    input_data = models.TextField(blank=True, null=True, verbose_name="Данные на входе")
    output_data = models.TextField(blank=True, null=True, verbose_name="Данные на выходе")
    result = models.SmallIntegerField(choices=RESULT, default=CREATED)
