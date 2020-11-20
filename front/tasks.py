from datetime import timedelta

from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from front import models, functions
# from front.functions import sendmail
from marathon.celery import app

from yandex_checkout import Configuration, Payment, WebhookNotification
from django.conf import settings
from os import path
import environ

app.conf.task_default_queue = 'default'

sett = models.Setting.objects.filter().first()


@app.task(name="front.tasks.check_registry_sent", ignore_result=True)
def check_registry_sent():
    """
        периодическая проверка неотправленных писем о регистрации
    """
    sett = models.Setting.objects.filter().first()
    accounts = models.Account.objects.exclude(registry_sent=True)
    for a in accounts:
        new_password = functions.generate_code(length=8)
        a.user.set_password(new_password)
        a.user.save()
        subject = 'Регистрация на платформе марафона "Движение Вверх"'
        mail_context = {"login": a.user.username,
                        "password": new_password,
                        "settings": sett,
                        "account": a}
        html_message = render_to_string('mail/registration.html', mail_context)
        # plain_message = strip_tags(html_message)
        send_email = models.sendmail(subject=subject, message=html_message, recipient_list=[a.user.email])
        if not send_email:
            a.registry_sent = False
            a.save()
        else:
            a.registry_sent = True
            a.save()


@app.task(name="front.tasks.check_payment_status", ignore_result=True)
def check_payment_status():
    """
    периодическая проверка неконечных статусов платежа, с момента создания которых прошел час
    (в течении часа пользователю доступен виджет оплаты в статусе -pending-)
    """
    payments = models.Payment.objects.filter(account__isnull=False, yuid__isnull=False).exclude(
        status__in=['succeeded', 'canceled'])
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
                    payment.status_set(payment_info.status)
                    # models.Payment.objects.filter(pk=payment.pk).update(status=payment_info.status)
                    # payment.status = payment_info.status
                    # if payment_info.status == 'succeeded':
                    #     payment.date_approve = timezone.now()
                    # payment.save()
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


def form_mail(lessons, text, subject, add_time=False, only_not_paid=False):
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

        # mail1 = f'<p>Не пропустите тему №{lesson.number} <b>"{lesson.title}"</b>!</p>' \
        #         f'<p>В личном кабинете <b>{lesson.date_publish.strftime("%d.%m.%Y")} в {lesson.date_publish.strftime("%H:%M")} МСК</b>!</p>'
        # mail2 = f'<p>Не пропустите новую тему №{lesson.number} <b>"{lesson.title}"</b>!</p>' \
        #         f'<p>В личном кабинете <b>{lesson.date_publish.strftime("%d.%m.%Y")} в {lesson.date_publish.strftime("%H:%M")} МСК</b>!</p>' \
        #         '<p>Вы ещё успеваете приобрести подписку на все темы марафона на сайте!</p>'
        # if add_time:
        #     text += f'<b>Завтра в {timezone.localtime(lesson.date_publish).strftime("%H:%M")} по моск. времени</b>'
        mail_context = {"settings": sett, "message": text}
        html_message = render_to_string('mail/new_lesson_notify.html', mail_context)

        for email in accounts_other:
            send_email = models.sendmail(subject=subject, message=html_message, recipient_list=[email])

        if not only_not_paid:
            for email in accounts_payd:
                send_email = models.sendmail(subject=subject, message=html_message, recipient_list=[email])


@app.task(name="front.tasks.clean_bots", ignore_result=True)
def clean_bots():
    """
        удаление аккаунтов, которые не подтвердили учетную запись в течение месяца

    """
    bots = models.Account.objects.filter(registry_sent=True, approved=False,
                                         date_registry__lt=timezone.now() - timedelta(days=90))
    for b in bots:
        b.user.delete()


@app.task(name="front.tasks.mass_email_send_before", ignore_result=True)
def mass_email_send_day_before():
    """
        периодическая отправка напоминаний о публикации темы 20:00 за день
    """
    lessons = models.Lesson.objects.filter(date_publish__date=(timezone.now() + timedelta(days=1)).date())
    if lessons:
        subject = 'Марафон "Движение Вверх"'
        text = f'<p>Вы стали участником марафона. Осталось сделать последний шаг. ' \
               f'Места ограничены! Не отдайте свой успех другому!</p>' \
               f'<p><a href="{sett.website}" target="_blank" style="font-weight: bold; color: #000">{sett.website}</a></p>' \
            # f'Завтра в 16:00 по моск. времени'
        form_mail(lessons, text, subject, add_time=True, only_not_paid=True)


@app.task(name="front.tasks.mass_email_send_today", ignore_result=True)
def mass_email_send_today():
    """
        периодическая отправка напоминаний о публикации темы 08:00 15:00 в день
    """
    lessons = models.Lesson.objects.filter(date_publish__date=timezone.now().date())
    if lessons:
        subject = 'Марафон "Движение Вверх"'
        text = f'<p>Уже сегодня ты узнаешь, к чему ты призван, в каком направлении развиваться. ' \
               f'Старт в 16:00 по (моск.времени). Не откладывай на завтра, твой успех тебя ждёт!</p>'
        form_mail(lessons, text, subject)


@app.task(name="front.tasks.mass_notify_for_not_paid", ignore_result=True)
def mass_notify_for_not_paid():
    """
        периодическая отправка напоминаний о покупке марафона, зарегистрировавшимся
    """

    subject = 'Марафон "Движение Вверх"'
    text = f'<p>Вы прошли удачно регистрацию на марафон успеха. ' \
           f'Первый урок «Точка опоры» уже ждёт вас в вашем личном кабинете ' \
           f'<a href="{sett.website}" target="_blank" style="font-weight: bold; color: #000">{sett.website}</a></p>' \
           f'<p>Не останавливайтесь!</p>'
    emails = models.Account.objects.exclude(payment__status="succeeded").values_list('user__email',
                                                                                     flat=True).distinct()
    mail_context = {"settings": sett, "message": text}
    html_message = render_to_string('mail/new_lesson_notify.html', mail_context)

    for email in emails:
        send_email = models.sendmail(subject=subject, message=html_message, recipient_list=email)


@app.task(name="front.tasks.start_mailing", ignore_result=True)
def start_mailing(pk):
    """
        рассылка
    """
    log = models.Logging.objects.create(action="start_mailing", input_data=pk)
    mailing = None
    try:
        mailing = models.Mailing.objects.get(pk=pk)
        if not mailing.active:
            raise Exception(f'mailing: {mailing.pk} is not active')
        if mailing.recipient == mailing.PAYED:
            if mailing.marathon:
                qset = models.Account.objects.filter(payment__marathon=mailing.marathon, payment__status="succeeded",
                                                     payment__date_approve__gte=timezone.now() - timedelta(days=62))
            else:
                qset = models.Account.objects.filter(payment__status="succeeded",
                                                     payment__date_approve__gte=timezone.now() - timedelta(days=62))
        elif mailing.recipient == mailing.NOT_PAYED:
            if mailing.marathon:
                qset = models.Account.objects.exclude(payment__marathon=mailing.marathon, payment__status="succeeded",
                                                      payment__date_approve__gte=timezone.now() - timedelta(days=62))
            else:
                qset = models.Account.objects.exclude(payment__status="succeeded",
                                                      payment__date_approve__gte=timezone.now() - timedelta(days=62))
        else:
            qset = models.Account.objects.all()

        emails = qset.values_list('user__email', flat=True).distinct()
        mail_context = {"settings": sett, "message": mailing.message}
        html_message = render_to_string('mail/new_lesson_notify.html', mail_context)
        attach = [mailing.attach.path] if mailing.attach else None

        for email in emails:
            send_mail.delay(
                subject=mailing.subject, message=html_message, recipient_list=email, attach=attach
            )
    except Exception as exc:
        log.output_data = exc
        log.result = log.FAIL
    else:
        log.result = log.SUCCESS
    finally:
        log.save()
        if mailing:
            mailing.active = False
            mailing.save(update_fields=('active',))


@app.task(name="front.tasks.send_mail", ignore_result=True)
def send_mail(subject, message, recipient_list, from_email=None, attach: iter = None):
    """
        отправка письма
    """
    models.sendmail(subject, message, recipient_list, from_email, attach)


@app.task(name="front.tasks.save_video", ignore_result=True)
def save_video():
    """
        периодическая проверка необходимости скачать видеофайлв качестве для урока
    """
    empty_videos = models.Video.objects.filter(lesson__isnull=False, link__isnull=False, url__isnull=True)
    if empty_videos.exists():
        for video in empty_videos:
            video.save()

