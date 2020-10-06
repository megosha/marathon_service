from datetime import timedelta

from django import template

register = template.Library()


@register.filter()
def get_value(dictionary, key):
    if dictionary and isinstance(dictionary, dict):
        try:
            val = dictionary.get(str(key))
        except:
            return None
        else:
            return val
    else:
        return None


@register.filter()
def full_status(payment):
    try:
        status = payment.status
    except:
        return None
    state = {'pending': 'Платёж создан (в обработке)',
            'waiting_for_capture': 'Платёж оплачен, деньги авторизованы и ожидают списания',
            'succeeded': 'Платёж успешно завершён',
             'canceled': 'Платёж отменён'}
    return state.get(status, 'Неизвестный статус')

@register.filter()
def deltatime(dt, deltadays):
    try:
        return dt + timedelta(days=int(deltadays))
    except:
        return None


@register.filter()
def title_general(title):
    return str(title).upper()[:str(title).rfind(' ')]

@register.filter()
def title_last(title):
    return str(title).upper()[str(title).rfind(' ')+1:]