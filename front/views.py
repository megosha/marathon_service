import json
from string import ascii_lowercase
import random
import environ
from os import path

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template

from django.views.generic import FormView
from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from front import models, forms

# Create your views here.

base_dir = settings.BASE_DIR

env = environ.Env()
env.read_env(path.join(base_dir, '.env'))

class ContextViewMixin(View):
    def make_context(self, context=None, **kwargs):
        if not context: context = {}
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        else:
            context['user'] = None
        # try:
        #     settings = models.Settings.objects.get()
        # except:
        #     context = {}
        # else:
        #     context = {'settings': settings}
        if kwargs:
            for k, v in kwargs.items():
                context[f'{k}'] = v
        return context

#todo feedback form for questions
class Index(ContextViewMixin):
    def get(self, request):
        context = self.make_context()
        return render(request, 'index.html', context=context)


LETTERS = ascii_lowercase
NUMBERS = ''.join(str(i) for i in range(10))

# todo refactor to functions file
def generate_code(length=16):
    bool_range = range(2)
    code = ''.join(map(lambda x: random.choice(NUMBERS) if random.choice(bool_range) else str.upper(
        random.choice(LETTERS)) if random.choice(bool_range) else random.choice(LETTERS), range(length)))
    return code

#todo template of registry
# в шаблоне сделать кнопку для перехода на страницу входа
# и кнопку для пометки ошибочной регистрации (по нажатию запрос на api и удаление из базы этого пользователя по почте)
@method_decorator(csrf_exempt, name='dispatch')
class Register(ContextViewMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return super(Register, self).dispatch(request)
        else:
            return HttpResponseRedirect('/me')

    def get(self, request, form=None):
        if form is None: form = forms.RegisterAccount()
        form_html = get_template('includes/form_register.html').render(context={"form": form}, request=request)
        context = self.make_context(form_html=form_html)
        return render(request, 'auth.html', context=context)

    def post(self, request):
        form = forms.RegisterAccount(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data.get("firstname")
            lastname = form.cleaned_data.get("lastname")
            phone = form.cleaned_data.get("phone")
            email = form.cleaned_data.get("email")
            ageconfirm = form.cleaned_data.get("ageconfirm")
            if not ageconfirm:
                form.errors['ageconfirm'] = "Этот флажок должен быть установлен"
            else:
                user, new = models.User.objects.get_or_create(username=email)
                if not new:
                    form.errors['custom'] = f"Пользователь с почтой {email} уже зарегистрирован"
                else:
                    user.first_name = firstname
                    user.last_name = lastname
                    user.email = email
                    password = generate_code(length=8)
                    user.set_password(password)
                    user.save()
                    account = models.Account.objects.create(user=user, phone=phone)

                    created = models.Account.objects.filter(user=user, phone=phone).exists()
                    if created:
                        subject = 'Регистрация на платформе марафона "Движение Вверх"'
                        message = f'Здравствуйте!\nВы успешно зарегистрированы на платформе марафона "Движение Вверх"\n\n' \
                                  f'Для входа в личный кабинет, используйте следующие дaнные:\n' \
                                  f'Логин: {email}\nПароль: "{password}"\n\n' \
                                  f'Внимание! не сообщайте никому данные для входа!'
                        from_email = env('FROM_EMAIL')
                        email_to = [email, ]
                        try:
                            send_mail(subject, message, from_email, email_to)
                        except Exception as err:
                            account.registry_sent = False
                            account.save()
                            print(err)
                        else:
                            account.registry_sent = True
                            account.save()
                            request.session['registry'] = f'Данные для входа в личный кабинет отправлены на {email}'
                            return HttpResponseRedirect('/login')
        return self.get(request, form=form)

#todo recovery password with email template
@method_decorator(csrf_exempt, name='dispatch')
class Login(ContextViewMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/me')

    def get(self, request, form=None):
        if form is None: form = forms.Login()
        registry = request.session.pop('registry') if 'registry' in request.session else None
        context_insert = {"form": form, "registry": registry}
        form_html = get_template('includes/form_login.html').render(context=context_insert, request=request)
        context = self.make_context(form_html=form_html)
        return render(request, 'auth.html', context=context)

    def post(self, request):
        form = forms.Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("login")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(self.request, user)
                return HttpResponseRedirect('/me')
            else:
                form.errors['custom'] = f"Неверный логин или пароль"
        return self.get(request, form=form)

class Logout(View):
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return HttpResponseRedirect("/")

#todo feedback
class Account(LoginRequiredMixin, ContextViewMixin):
# class Account(View):
    def get(self, request):
        # redirect_field_name = 'redirect_to'
        context = self.make_context(tmp='qwe qweqwe qwe')
        return render(request, 'account_ready.html', context=context)
