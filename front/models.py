from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=18, blank=False, null=False, verbose_name="Контактный телефон")
    photo = models.FileField(upload_to='images/avatars/', blank=True, verbose_name="Аватар")
    feedback = models.TextField(null=True, blank=True, verbose_name="Отзыв")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    registry_date = models.DateTimeField(auto_now=True, verbose_name="Дата публикации новости")
    registry_sent = models.BooleanField(default=None, blank=True, null=True, verbose_name="Письмо о регистрации отправлено")
    description = models.TextField(verbose_name="Комментарий", default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()}"



