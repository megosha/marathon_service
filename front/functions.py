import json
from string import ascii_lowercase
import random
import environ
from os import path

from django.core.mail import send_mail
from django.conf import settings



base_dir = settings.BASE_DIR
medis_dir = settings.MEDIA_ROOT

env = environ.Env()
env.read_env(path.join(base_dir, '.env'))

LETTERS = ascii_lowercase
NUMBERS = ''.join(str(i) for i in range(10))


def generate_code(length=16):
    bool_range = range(2)
    code = ''.join(map(lambda x: random.choice(NUMBERS) if random.choice(bool_range) else str.upper(
        random.choice(LETTERS)) if random.choice(bool_range) else random.choice(LETTERS), range(length)))
    return code


def sendmail(subject, message, recipient_list, from_email=None, fail_silently=False, html_message=None):
    if from_email is None:
        from_email = env('FROM_EMAIL')
    try:
        send_mail(subject=subject, message=message, from_email=from_email,
                  recipient_list=recipient_list, fail_silently=fail_silently, html_message=html_message)
    except Exception as err:
        # todo Logging
        print(err)
        return False
    else:
        return True



