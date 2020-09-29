# TODO payment.status != success and != success canceled
# TODO payment.status_mail_invoice and success
# TODO payment.status_mail_lesson and payment.marathon.lesson_set.filter(date_publish-timezone.now<1)
# TODO account.registry_sent == False
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from front import models
from front.functions import sendmail

from yandex_checkout import Configuration, Payment, WebhookNotification


def check_payment_status():
    """
    периодическая проверка неконечных статусов платежа, с момента создания которых прошел час
    (в течении часа пользователю доступен виджет оплаты в статусе -pending-)
    """
    payments = models.Payment.objects.filter(date_pay__gte=timezone.now() + timedelta(hours=1)).exclude(
        status__in=['succeeded', 'canceled'])
    if payments:
        for payment in payments:
            payment_info = Payment.find_one(payment.yuid)
            if payment.status != payment_info.status:
                models.Payment.objects.filter(pk=payment.pk).update(status=payment_info.status)
                payment.status = payment_info.status
                if payment_info.status == 'succeeded':
                    payment.date_approve = timezone.now()
                payment.save()
