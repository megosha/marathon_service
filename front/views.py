from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template

from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from front import models, forms, functions


# Create your views here.


class ContextViewMixin(View):
    def make_context(self, context=None, **kwargs):
        if not context: context = {}
        if self.request.user.is_authenticated and models.Account.objects.filter(user=self.request.user).exists():
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


# todo feedback form for questions
class Index(ContextViewMixin):
    def get(self, request):
        context = self.make_context()
        return render(request, 'index.html', context=context)


# todo в шаблоне сделать кнопку для пометки ошибочной регистрации (по нажатию запрос на api и удаление из базы этого пользователя по почте)
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
        context = self.make_context(form_html=form_html, title='Регистрация')
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
                    password = functions.generate_code(length=8)
                    user.set_password(password)
                    user.save()
                    account = models.Account.objects.create(user=user, phone=phone)

                    created = models.Account.objects.filter(user=user, phone=phone).exists()
                    if created:
                        subject = 'Регистрация на платформе марафона "Движение Вверх"'
                        settings = models.Setting.objects.filter().first()
                        mail_context = {"login": email,
                                        "password": password,
                                        "settings": settings}
                        html_message = render_to_string('mail/registration.html', mail_context)
                        plain_message = strip_tags(html_message)
                        send_email = functions.sendmail(subject=subject, message=plain_message, recipient_list=[email],
                                                        html_message=html_message)
                        if not send_email:
                            account.registry_sent = False
                            account.save()
                        else:
                            account.registry_sent = True
                            account.save()
                            request.session['registry'] = f'Данные для входа в личный кабинет отправлены на {email}'
                            return HttpResponseRedirect('/login')
        return self.get(request, form=form)


# todo recovery password with email template
@method_decorator(csrf_exempt, name='dispatch')
class Login(ContextViewMixin):
    def dispatch(self, request, *args, **kwargs):
        if not (self.request.user.is_authenticated and models.Account.objects.filter(user=self.request.user).exists()):
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/me')

    def get(self, request, form=None):
        if form is None: form = forms.Login()
        registry = request.session.pop('registry') if 'registry' in request.session else None
        context_insert = {"form": form, "registry": registry}
        form_html = get_template('includes/form_login.html').render(context=context_insert, request=request)
        context = self.make_context(form_html=form_html, title='Вход')
        return render(request, 'auth.html', context=context)

    def post(self, request):
        form = forms.Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("login")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(self.request, user)
                if models.Account.objects.filter(user=self.request.user).exists():
                    user.account.approved = True
                    user.account.save()
                return HttpResponseRedirect('/me')
            else:
                form.errors['custom'] = f"Неверный логин или пароль"
        return self.get(request, form=form)


class Logout(View):
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return HttpResponseRedirect("/")


class ResetPassword(ContextViewMixin):
    def get(self, request, form=None):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/me')
        if form is None:
            form = forms.ResetPWD()

        context_insert = {'form': form, 'title': "Сброс пароля"}
        form_html = get_template('includes/form_reset.html').render(context=context_insert, request=request)
        context = self.make_context(form_html=form_html, title='Сброс пароля')
        return render(request, 'auth.html', context=context)

    def post(self, request):
        if request.user.is_authenticated: return HttpResponseRedirect('/me')
        form = forms.ResetPWD(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            account = models.Account.objects.filter(user__email=email).first()
            if not account:
                form.errors['custom'] = "Пользователь с таким email не найден."
            else:
                password = functions.generate_code(length=8)
                account.user.set_password(password)
                try:
                    account.user.save()
                except:
                    form.errors['custom'] = "Ошибка при сбросе пароля. Повторите попытку позднее."
                else:
                    subject = 'Сброс пароля в личном кабинете марафона "Движение Вверх"'
                    settings = models.Setting.objects.filter().first()
                    mail_context = {"login": email,
                                    "password": password,
                                    "settings": settings}
                    html_message = render_to_string('mail/reset.html', mail_context)
                    plain_message = strip_tags(html_message)
                    send_email = functions.sendmail(subject=subject, message=plain_message, recipient_list=[email],
                                                    html_message=html_message)
                    if not send_email:
                        form.errors['custom'] = "Ошибка при сбросе пароля. Повторите попытку позднее."
                        # todo писать в таблицу ошибок или логов
                    else:
                        form_html = get_template('includes/reset_redirect.html').render(context={'email': email},
                                                                                        request=request)
                        context = self.make_context(form_html=form_html, title='Сброс пароля')
                        return render(request, "auth.html", context)
        return self.get(request, form=form)


# todo feedback
class Account(LoginRequiredMixin, ContextViewMixin):
    # class Account(View):
    def dispatch(self, request, *args, **kwargs):
        if models.Account.objects.filter(user=self.request.user).exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/')

    def get(self, request):
        # redirect_field_name = 'redirect_to'
        context = self.make_context()
        return render(request, 'account_ready.html', context=context)
