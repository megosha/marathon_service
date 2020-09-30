# TODO payment.status != success and != success canceled
# TODO payment.status_mail_invoice and success
# TODO payment.status_mail_lesson and payment.marathon.lesson_set.filter(date_publish-timezone.now<1)
# TODO account.registry_sent == False
from datetime import timedelta

from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from front import models
from front.functions import sendmail
from marathon.celery import app

from yandex_checkout import Configuration, Payment, WebhookNotification
from django.conf import settings
from os import path
import environ

app.conf.task_default_queue = 'default'


@app.task(name="front.tasks.check_payment_status", ignore_result=True)
def check_payment_status():
    """
    периодическая проверка неконечных статусов платежа, с момента создания которых прошел час
    (в течении часа пользователю доступен виджет оплаты в статусе -pending-)
    """
    payments = models.Payment.objects.exclude(account__isnull=True, status__in=['succeeded', 'canceled'])
    if payments:
        try:
            upper_settings = models.UpperSetting.objects.get()
            test = upper_settings.test_mode
            if test:
                yandex_api_key = upper_settings.yandex_api_key_test
                shopid = upper_settings.shopid_test
            else:
                yandex_api_key = upper_settings.yandex_api_key
                shopid = upper_settings.shopid
        except:
            base_dir = settings.BASE_DIR

            env = environ.Env()
            env.read_env(path.join(base_dir, '.env'))
            yandex_api_key = env('YANDEX_API_KEY')
            shopid = env('SHOPID')
        Configuration.account_id = shopid
        Configuration.secret_key = yandex_api_key
        for payment in payments:
            try:
                payment_info = Payment.find_one(payment.yuid)
                if payment.status != payment_info.status:
                    models.Payment.objects.filter(pk=payment.pk).update(status=payment_info.status)
                    payment.status = payment_info.status
                    if payment_info.status == 'succeeded':
                        payment.date_approve = timezone.now()
                    payment.save()
            except Exception as ex:
                print(ex)


@app.task(name="front.tasks.check_invoice_sent", ignore_result=True)
def check_invoice_sent():
    """
        периодическая проверка неотправленных чеков
    """
    payments = models.Payment.objects.filter(invoice__isnull=False).exclude(status_mail_invoice=True)
    for payment in payments:
        payment.send_invoice()
        payment.save()


def form_mail(lessons):
    for lesson in lessons:
        accounts = models.Account.objects.prefetch_related('payment_set', 'payment_set__marathon__lesson_set').all()
        lesson.marathon.payment_set.all().values('account', 'status', 'date_approve')
        accounts_payd = []
        accounts_other = []
        for account in accounts:
            if account.payment_set.filter(marathon__lesson=lesson, status="succeeded",
                                          date_approve__gte=timezone.now() - timedelta(days=62)).exists():
                accounts_payd.append(account.user.email)
            else:
                accounts_other.append(account.user.email)

        subject = 'Новый вебинар марафона "Движение Вверх"'
        mail1 = f'<p>Не пропустите тему №{lesson.number} <b>"{lesson.title}"</b>!</p>' \
                f'<p>В личном кабинете <b>{lesson.date_publish.strftime("%d.%m.%Y")} в {lesson.date_publish.strftime("%H:%M")} МСК</b>!</p>'
        mail2 = f'<p>Не пропустите новую тему №{lesson.number} <b>"{lesson.title}"</b>!</p>' \
                f'<p>В личном кабинете <b>{lesson.date_publish.strftime("%d.%m.%Y")} в {lesson.date_publish.strftime("%H:%M")} МСК</b>!</p>' \
                '<p>Вы ещё успеваете приобрести подписку на все темы марафона на сайте!</p>'
        sett = models.Setting.objects.filter().first()
        mail_context = {"settings": sett, "message": mail1}
        html_message = render_to_string('mail/new_lesson_notify.html', mail_context)
        for email in accounts_payd:
            send_email = sendmail(subject=subject, message=html_message, recipient_list=[email])
        mail_context = {"settings": sett, "message": mail2}
        html_message = render_to_string('mail/news.html', mail_context)
        for email in accounts_other:
            send_email = sendmail(subject=subject, message=html_message, recipient_list=[email])


@app.task(name="front.tasks.mass_email_send_before", ignore_result=True)
def mass_email_send_day_before():
    """
        периодическая отправка напоминаний о публикации темы 20:00 за день
    """
    lessons = models.Lesson.objects.filter(date_publish__date=(timezone.now() + timedelta(days=1)).date())
    if lessons:
        form_mail(lessons)


@app.task(name="front.tasks.mass_email_send_today", ignore_result=True)
def mass_email_send_today():
    """
        периодическая отправка напоминаний о публикации темы 08:00 15:00 в день
    """
    lessons = models.Lesson.objects.filter(date_publish__date=timezone.now().date())
    if lessons:
        form_mail(lessons)