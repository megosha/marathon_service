from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from front import models
# from front.functions import sendmail

# class Request():
#     user = None

class Command(BaseCommand):
    def handle(self, *args, **options):
        emails = list(
            models.Account.objects.all().exclude(user__username='mv').values_list('user__email', flat=True))
        subject = 'Новости марафона "Движение Вверх"'
        msg_safe = '<p>На сайте стартовала возможность приобрести подписку на марафон.</p>' \
                   '<p>А также, в личном кабинете уже доступен для просмотра базовый бесплатный урок!</p>'
        sett = models.Setting.objects.filter().first()
        mail_context = {"settings": sett, "message": msg_safe}
        html_message = render_to_string('mail/news.html', mail_context)
        for email in emails:
            try:
                send_email = models.sendmail(subject=subject, message=html_message, recipient_list=[email])
            except:
                pass