import datetime
from os import path
import uuid
import json
import environ

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.template.loader import get_template
from django.utils import timezone

from front import models, functions
from front.views import ContextViewMixin

from yandex_checkout import Configuration, Payment, WebhookNotification
from yandex_checkout.domain.common.base_object import BaseObject

# Create your views here.


try:
    upper_settings = models.UpperSetting.objects.get()
    test = upper_settings.test_mode
    if test:
        yandex_api_key = upper_settings.yandex_api_key_test
        shopid = upper_settings.shopid_test
    else:
        yandex_api_key = upper_settings.yandex_api_key
        shopid = upper_settings.shopid
    return_url = upper_settings.return_url
except:
    base_dir = settings.BASE_DIR

    env = environ.Env()
    env.read_env(path.join(base_dir, '.env'))
    yandex_api_key = env('YANDEX_API_KEY')
    shopid = env('SHOPID')
    return_url = env('RETURN_URL')


class YandexPayment(LoginRequiredMixin, ContextViewMixin):
    def get(self, request):
        if not models.Account.objects.filter(user=self.request.user).exists():
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/me')

    def post(self, request, marathon_id):
        user = self.request.user
        if not models.Account.objects.filter(user=user).exists():
            return HttpResponseRedirect('/')

        log = models.Logging.objects.create(action="Создание платежа в Яндекс кассе. api/views.YandexPayment.post()")
        account = user.account
        result = {}

        # lesson_num = request.POST.get('open_widget')

        try:
            marathon = models.Marathon.objects.get(pk=marathon_id)
            # есть ли актуальный (не просроченный) платеж за урок
            earlyer_pay = models.Payment.objects.filter(
                account=account, marathon=marathon, date_approve__gte=timezone.now() - datetime.timedelta(days=62)
            ).exists()
            if earlyer_pay:
                raise Exception('Payment exists')
        except:
            result['error'] = 'Ошибка данных для формирования нового платежа'
            return HttpResponseRedirect('/me')

        if marathon.cost == 0:
            try:
                new_payment = models.Payment.objects.create(account=account,
                                                        marathon=marathon,
                                                        date_pay=timezone.now(),
                                                        date_approve=timezone.now(),
                                                        status="succeeded")
                log.input_data = f"account {account.user.username}\nmarathon {marathon.pk}\ntime  {timezone.now()}\n"
                log.output_data = f"payment_pk {new_payment.pk},\nuuid {new_payment.pk}"
                log.result = log.SUCCESS
                log.save()
            except Exception as exc:
                log.result = log.FAIL
                log.output_data = f"{exc}"
                log.save()

            return HttpResponseRedirect(f'/me?marathon={marathon.pk}')

        try:
            idempotence_key = uuid.uuid4()
            Configuration.account_id = shopid
            Configuration.secret_key = yandex_api_key
            payment_params = {
                "amount": {
                    "value": f"{marathon.cost}.00",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "embedded"
                },
                "capture": True,
                "description": f"Марафон {marathon.title[:75]}",
                "receipt": {
                    "customer": {
                        "full_name": f"{account.user.get_full_name()}",
                        "phone": f"{account.phone}",
                        "email": f"{account.user.email}",
                    },
                    "items": [
                        {
                            "description": f"Марафон {marathon.title[:75]}",
                            "quantity": "1.00",
                            "amount": {
                                "value": f"{marathon.cost}.00",
                                "currency": "RUB"
                            },
                            "vat_code": "1",
                            # TODO    1-Без НДС 2-НДС по ставке 0% 3-НДС по ставке 10% 4-НДС чека по ставке 20% 5-НДС чека по расчетной ставке 10/110 6 	НДС чека по расчетной ставке 20/120
                            "payment_mode": "full_prepayment",
                            "payment_subject": "intellectual_activity",
                            "save_payment_method": False,
                            # "receipt_phone":""
                        }
                    ]
                }}
            payment = Payment.create(payment_params, idempotence_key)
            payment_dict = {key: value.__dict__ if isinstance(value, BaseObject) else value for key, value in
                            payment.__dict__.items()}
            log.input_data = f"{shopid}\n{yandex_api_key}\n{payment_params}\n{idempotence_key}"
        except Exception as err:
            log.result = log.FAIL
            log.output_data = f"{err}"
            log.save()
        else:
            new_payment = models.Payment.objects.create(uuid=idempotence_key,
                                                        amount=marathon.cost,
                                                        account=account,
                                                        marathon=marathon,
                                                        request=f"{shopid}\n{yandex_api_key}\n{payment_params}\n{idempotence_key}",
                                                        response=f"{payment_dict}",
                                                        yuid=payment.id,
                                                        status=payment.status,
                                                        confirmation_token=payment.confirmation.confirmation_token)
            log.result = log.SUCCESS
            log.output_data = f"{payment_dict}"
            log.save()
            return HttpResponseRedirect(f'/api/payment/widget/{idempotence_key}')
        return HttpResponseRedirect(f'/me')


class WidgetRender(LoginRequiredMixin, ContextViewMixin):
    def get(self, request, uuid):
        log = models.Logging.objects.create(action="Рендер виджета оплаты в Яндекс кассе. api/views.WidgetRender.get()")
        try:
            payment = models.Payment.objects.get(uuid=uuid)
            log.input_data = f"uuid платежа: {uuid}"
        except Exception as err:
            context = self.make_context(error="Ошибка. Платеж не найден.")
            log.result = log.FAIL
            log.output_data = f"{err}"
            log.save()
            return render(request, 'general.html', context=context)
        else:
            context = self.make_context(confirmation_token=payment.confirmation_token, return_url=return_url)
            request.session['payment'] = f"{uuid}"
            log.result = log.SUCCESS
            log.save()
            return render(request, 'widget_yandex.html', context=context)


class PaymentReturnUrl(ContextViewMixin):
    def get(self, request):
        uuid = request.session.pop('payment') if 'payment' in request.session else None
        payment = None
        if uuid is not None:
            payment = models.Payment.objects.filter(uuid=uuid).first()
            if payment:
                payment_id = payment.yuid
                log = models.Logging.objects.create(
                    action="Запрос данных в Яндекс кассе для ReturnUrl после оплаты. api/views.PaymentReturnUrl.get()",
                    input_data=f"yuid: {payment_id}")
                try:
                    payment_info = Payment.find_one(payment_id)
                except Exception as err:
                    log.result = log.FAIL
                    log.output_data = f"{err}"
                    log.save()
                else:
                    if payment.status != payment_info.status:
                        payment.status_set(payment_info.status)
                        # models.Payment.objects.filter(pk=payment.pk).update(status=payment_info.status)
                        # payment.status = payment_info.status
                        # if payment_info.status == 'succeeded':
                        #     payment.date_approve = timezone.now()
                        # payment.save()
                    log.result = log.SUCCESS
                    try:
                        payment_info_dict = {key: value.__dict__ if isinstance(value, BaseObject) else value for key, value
                                        in payment_info.__dict__.items()}
                        log.output_data = f"{payment_info_dict}"
                    except:
                        log.output_data = f"{payment_info}"
                    log.save()
        form_html = get_template('includes/payment_info.html').render(context={'payment': payment}, request=request)
        context = self.make_context(content=form_html, title='Статус платежа')
        return render(request, 'general.html', context=context)


class YandexNotify(ContextViewMixin):
    def base(self, request):
        log = models.Logging.objects.create(
            action="Входящее уведомление от Яндекс Кассы. api/views.YandexNotify.base()")
        # Cоздайте объект класса уведомлений в зависимости от события
        try:
            event_json = json.loads(request.body)
            notification_object = WebhookNotification(event_json)
            log.input_data = f"request.body: {event_json}"
        except Exception as err:
            log.result = log.FAIL
            log.output_data = f"{err}"
            log.save()
            # обработка ошибок
            return HttpResponse(status=500)

        # Получите объекта платежа
        payment = notification_object.object

        log.result = log.SUCCESS
        try:
            payment_dict = {key: value.__dict__ if isinstance(value, BaseObject) else value for key, value
                                 in payment.__dict__.items()}
            log.output_data = f"{payment_dict}"
        except:
            log.output_data = f"{payment}"
        log.save()
        payment_obj = models.Payment.objects.filter(yuid=payment.id).first()
        if payment_obj and payment_obj.status != payment.status:
            payment_obj.status_set(payment.status)
            # models.Payment.objects.filter(pk=payment_obj.pk).update(status=payment.status)
            # payment_obj.status = payment.status
            # if payment.status == 'succeeded':
            #     payment_obj.date_approve = timezone.now()
            # payment_obj.save()

        return HttpResponse(status=200)

    def get(self, request):
        return self.base(request)

    def post(self, request):
        return self.base(request)
