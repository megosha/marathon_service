from string import ascii_lowercase
# import json
# import random
# import environ
# from os import path

# from django.core.mail import EmailMultiAlternatives
# from django.conf import settings
from django.utils.crypto import get_random_string






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

# def sendmail(subject, message, recipient_list, from_email=None, attach: iter=None):
#     pass



