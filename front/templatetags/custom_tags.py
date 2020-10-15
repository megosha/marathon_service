from datetime import timedelta

from django import template

from celery import task
from django.utils.safestring import mark_safe

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


@register.simple_tag
def processes_queue():
    html = 'Очередь рассылок: <table><thead><tr>'
    i = task.control.inspect()
    q = i.scheduled()
    for k, v in q.items():
        html += f'<th>Процесс: {k}</th></tr></thead>'
        html += f'<thead><tr><th>Дата</th><th>Имя функции</th><th>ID рассылки</th></tr></thead>'
        for item in v:
            html += f'<tr><td>{item.get("eta")}</td><td>{item.get("request",{}).get("name")}</td><td>{item.get("request",{}).get("args")}</td></tr>'
    html += '</tr></table>'
    return mark_safe(html)


a = {'celery@marathon_dev': [{'eta': '2020-10-15T07:32:07.932717+00:00', 'priority': 6,
                              'request': {'id': '29b24aa9-b8d7-43aa-973f-65adca9197ba',
                                          'name': 'front.tasks.start_mailing', 'args': [4], 'kwargs': {},
                                          'type': 'front.tasks.start_mailing', 'hostname': 'celery@marathon_dev',
                                          'time_start': None, 'acknowledged': False,
                                          'delivery_info': {'exchange': '', 'routing_key': 'default', 'priority': 0,
                                                            'redelivered': None}, 'worker_pid': None}}]}
