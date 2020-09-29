# TODO payment.status != success and != success canceled
# TODO payment.status_mail_invoice and success
# TODO payment.status_mail_lesson and payment.marathon.lesson_set.filter(date_publish-timezone.now<1)
# TODO account.registry_sent == False
from front import models
from front.functions import sendmail

# def check_payment_status():
#     payments = models.Payment.objects




