import json
from string import ascii_lowercase
import random
import environ
from os import path

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.crypto import get_random_string



base_dir = settings.BASE_DIR
medis_dir = settings.MEDIA_ROOT

env = environ.Env()
env.read_env(path.join(base_dir, '.env'))

LETTERS = ascii_lowercase
NUMBERS = ''.join(str(i) for i in range(10))
# models.User.objects.make_random_password(length=8)

def generate_code(length=16):
    # bool_range = range(2)
    # code = ''.join(map(lambda x: random.choice(NUMBERS) if random.choice(bool_range) else str.upper(
    #     random.choice(LETTERS)) if random.choice(bool_range) else random.choice(LETTERS), range(length)))
    # code = '33662345'
    code = get_random_string(length=length)
    invalid_code = code.isdigit() or code.isalpha() or code.islower() or code.isupper()
    if invalid_code:
        while invalid_code:
            code = get_random_string(length=length)
            invalid_code = code.isdigit() or code.isalpha() or code.islower() or code.isupper()
    return code


def sendmail(subject, message, recipient_list, from_email=None, attach: iter=None):
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
    try:
        mail.send(fail_silently=False)
    except Exception as ex:
        print(ex)
        return False
    else:
        return True
    # try:
    #     send_mail(subject=subject, message=message, from_email=from_email,
    #               recipient_list=recipient_list, fail_silently=fail_silently, html_message=html_message)
    # except Exception as err:
    #     # todo Logging
    #     print(err)
    #     return False
    # else:
    #     return True



