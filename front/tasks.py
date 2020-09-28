# TODO payment.status != success and != success canceled
# TODO payment.status_mail_invoice and success
# TODO payment.status_mail_lesson and payment.marathon.lesson_set.filter(date_publish-timezone.now<1)
# TODO account.registry_sent == False
from django.template.loader import render_to_string

from front import models
from front.functions import sendmail


def news():
    emails = list(models.Account.objects.all().exclude(user__username='mv').values_list('user__email', flat=True))
    subject = 'Новости марафона "Движение Вверх"'
    msg_safe = '<p>На сайте стартовала возможность приобрести подписку на марафон.</p>' \
               '<p>А также, в личном кабинете уже доступен для просмотра базовый бесплатный урок!</p>'
    sett = models.Setting.objects.filter().first()
    mail_context = {"settings":sett, "message": msg_safe}
    html_message = render_to_string('mail/news.html', mail_context)
    try:
        send_email = sendmail(subject=subject, message=html_message, recipient_list=emails)
    except:
        pass
