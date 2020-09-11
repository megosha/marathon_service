from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.db.models import Exists, OuterRef
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template

from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from front import models, forms, functions


# import environ
# from django.conf import settings as sett
# from os import path


# base_dir = sett.BASE_DIR
#
# env = environ.Env()
# env.read_env(path.join(base_dir, '.env'))


# Create your views here.

class ContextViewMixin(View):
    def make_context(self, context=None, **kwargs):
        if not context: context = {}
        if self.request.user.is_authenticated and models.Account.objects.filter(user=self.request.user).exists():
            context['user'] = self.request.user
        else:
            context['user'] = None
        if kwargs:
            for k, v in kwargs.items():
                context[f'{k}'] = v
        return context


class PostRequiredMixin(ContextViewMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.method != "POST":
            return HttpResponseRedirect('/')
        return super().dispatch(request, *args, **kwargs)


class Test(ContextViewMixin):
    def get(self, request):
        form_html = get_template('includes/reset_redirect.html').render(context={'email': 'qwe'},
                                                                        request=request)
        context = self.make_context(form_html=form_html, title='Сброс пароля')
        return render(request, "auth.html", context)


class Index(ContextViewMixin):
    def base(self, request, form=None):
        if form is None: form = forms.Feedback()
        reviews = models.Feedback.objects.all()[:30]
        settings = models.Setting.objects.get()
        feedback = request.session.pop('feedback') if 'feedback' in request.session else False
        context = self.make_context(form=form,
                                    reviews=reviews,
                                    settings=settings,
                                    feedback=feedback)
        return render(request, 'index.html', context=context)

    def get(self, request, form=None):
        return self.base(request, form)

    def post(self, request):
        form = forms.Feedback(request.POST)
        if form.is_valid():
            fields = {'firstname': 'Имя', 'contact': 'Контакты', 'message': 'Сообщение'}
            message = ''
            for k, v in form.cleaned_data.items():
                message += f'{fields.get(k)}: "{v}"\n'
            subject = 'Новое сообщение по обратной связи  марафона "Движение Вверх"'
            settings = models.Setting.objects.filter().first()
            if not settings:
                form.errors['custom'] = f"При отправке сообщения произошла ошибка. Повторите попытку позднее."
                return self.base(request, form)
            email = settings.contact_mail
            send_email = functions.sendmail(subject=subject, message=message, recipient_list=[email], )
            if not send_email:
                form.errors['custom'] = f"При отправке сообщения произошла ошибка. Повторите попытку позднее."
            else:
                request.session['feedback'] = True
                return HttpResponseRedirect('/#feedback-label')
        return self.base(request, form)


@method_decorator(csrf_exempt, name='dispatch')
class Register(ContextViewMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return super(Register, self).dispatch(request)
        else:
            return HttpResponseRedirect('/me')

    def base(self, request, form=None):
        if form is None: form = forms.RegisterAccount()
        form_html = get_template('includes/form_register.html').render(context={"form": form}, request=request)
        context = self.make_context(form_html=form_html, title='Регистрация')
        return render(request, 'auth.html', context=context)

    def get(self, request, form=None):
        return self.base(request, form)

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
                    # # todo вынести привязку привязку марафона в оплату темы марафона
                    # marathone = models.Marathon.objects.filter().first()
                    account = models.Account.objects.create(user=user, phone=phone)

                    created = models.Account.objects.filter(user=user, phone=phone).exists()
                    if created:
                        # account.marathone.add(marathone)
                        subject = 'Регистрация на платформе марафона "Движение Вверх"'
                        settings = models.Setting.objects.filter().first()
                        mail_context = {"login": email,
                                        "password": password,
                                        "settings": settings,
                                        "account": account}
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
                    else:
                        user.delete()
        return self.base(request, form=form)


@method_decorator(csrf_exempt, name='dispatch')
class Login(ContextViewMixin):
    def dispatch(self, request, *args, **kwargs):
        if not (self.request.user.is_authenticated and models.Account.objects.filter(user=self.request.user).exists()):
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/me')

    def base(self, request, form=None):
        if form is None: form = forms.Login()
        registry = request.session.pop('registry') if 'registry' in request.session else None
        context_insert = {"form": form, "registry": registry}
        form_html = get_template('includes/form_login.html').render(context=context_insert, request=request)
        context = self.make_context(form_html=form_html, title='Вход')
        return render(request, 'auth.html', context=context)

    def get(self, request, form=None):
        return self.base(request, form)

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
        return self.base(request, form=form)


class Logout(View):
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return HttpResponseRedirect("/")


class RemoveAccount(LoginRequiredMixin, ContextViewMixin):
    # todo ставить признак, удалять если не был совершён вход в течении 2 недель
    def post(self, request):
        if models.Account.objects.filter(user=self.request.user).exists():
            subject = 'Удаление профиля на платформе марафона "Движение Вверх"'
            settings = models.Setting.objects.filter().first()
            mail_context = {"login": self.request.user.email,
                            "settings": settings}
            html_message = render_to_string('mail/remove.html', mail_context)
            plain_message = strip_tags(html_message)
            send_email = functions.sendmail(subject=subject, message=plain_message,
                                            recipient_list=[self.request.user.email],
                                            html_message=html_message)
            if not send_email:
                return JsonResponse({'sendmail': send_email})
                # todo писать в таблицу ошибок или логов
            else:
                self.request.user.delete()
                return JsonResponse({'sendmail': send_email, "deleted": True})
        return HttpResponseRedirect('/')


class ResetPassword(ContextViewMixin):
    def base(self, request, form=None):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/me')
        if form is None:
            form = forms.ResetPWD()
        context_insert = {'form': form, 'title': "Сброс пароля"}
        form_html = get_template('includes/form_reset.html').render(context=context_insert, request=request)
        context = self.make_context(form_html=form_html, title='Сброс пароля')
        return render(request, 'auth.html', context=context)

    def get(self, request, form=None):
        return self.base(request, form)

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
        return self.base(request, form=form)


# todo feedback
class Account(LoginRequiredMixin, ContextViewMixin):
    # class Account(View):
    # def dispatch(self, request, *args, **kwargs):
    #     if models.Account.objects.filter(user=self.request.user).exists():
    #         return super().dispatch(request, *args, **kwargs)
    #     else:
    #         return HttpResponseRedirect('/')

    # def base(self, request, form=None, context=None):
    #     if not models.Account.objects.filter(user=self.request.user).exists():
    #         return HttpResponseRedirect('/')
    #     return render(request, 'account_ready.html', context=context)

    def get(self, request, form=None):
        if not models.Account.objects.filter(user=self.request.user).exists():
            return HttpResponseRedirect('/')
        account: models.Account = request.user.account
        marathon = request.GET.get('marathon')
        marathon = models.Marathon.objects.filter(pk=marathon).first()
        marathones = models.Marathon.objects.filter(lesson__payment__account=account).distinct()
        if marathones.count() == 1 and marathon is None:
            marathon = models.Marathon.objects.filter().first()
        if marathon:
            # есть ли актуальный (не просроченный) платеж за урок
            paid_allowed = account.payment_set.filter(lesson=OuterRef('id'),
                                                      date_approve__gte=datetime.now() - timedelta(days=62))
            # причина отсутсивя доступа: True если просрочен платеж, False, если платежа не было
            paid_expired = account.payment_set.filter(lesson=OuterRef('id'),
                                                      date_approve__lt=datetime.now() - timedelta(days=62))
            lessons = models.Lesson.objects.filter(marathon=marathon, date_publish__lte=datetime.now()).annotate(
                paid=Exists(paid_allowed), expired=Exists(paid_expired)).order_by('number')
        else:
            lessons = []
        context = self.make_context(marathon=marathon,
                                    lessons=lessons,
                                    marathones=marathones)
        return render(request, 'account_ready.html', context=context)

    # def post(self, request):
    #     """ для отзывов """
    #     return self.base(request, form=form)
