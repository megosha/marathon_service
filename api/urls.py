from django.urls import path

from api import views

prefix = 'payment'

urlpatterns = [
    path(f'{prefix}/<int:marathon_id>', views.YandexPayment.as_view()),
    path(f'{prefix}/widget/<str:uuid>', views.WidgetRender.as_view()),
    path(f'{prefix}/finish', views.PaymentReturnUrl.as_view()),
    path(f'{prefix}/yandex_notify', views.YandexNotify.as_view()),
]

