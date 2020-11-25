import math
from datetime import datetime, timedelta
from django.utils import timezone

from django.contrib.auth import authenticate, login, logout
from django.db.models import Exists, OuterRef, F, Q, Value, Subquery
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.template.loader import get_template

from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.static import serve

from front import models, forms, functions

# import environ
from django.conf import settings as cnf
from os import path

from PIL import Image, ExifTags


# base_dir = sett.BASE_DIR
#
# env = environ.Env()
# env.read_env(path.join(base_dir, '.env'))


# Create your views here.

@login_required
def get_invoice(request, filename):
    try:
        payment = request.user.account.payment_set.all().filter(uuid=filename)
    except:
        return HttpResponseNotFound()
    if payment:
        load_path = path.join(cnf.MEDIA_ROOT, 'invoice')
        if path.isfile(path.join(load_path, f"{filename}.pdf")):
            return serve(request, f"{filename}.pdf", load_path)
    return HttpResponseNotFound()


@login_required
def get_hometask(request, marathon_pk, lesson_number):
    try:
        lesson = models.Lesson.objects.filter(marathon__pk=marathon_pk, number=lesson_number).first()
        hometask_file = lesson.hometask_file.file.name
    except:
        return HttpResponseNotFound()
    else:
        if path.isfile(hometask_file):
            return serve(request, f"{hometask_file}", '/')
        return HttpResponseNotFound()


@login_required
def get_gift(request, marathon):
    try:
        gift_file = models.Marathon.objects.filter(pk=marathon).first().gift.file.file.name
    except:
        return HttpResponseNotFound()
    if path.isfile(gift_file):
            return serve(request, f"{gift_file}", '/')
    return HttpResponseNotFound()

class ContextViewMixin(View):
    def make_context(self, context=None, **kwargs):
        if not context: context = {}
        context['current_date'] = timezone.now()
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
        reviews = models.Feedback.objects.filter(kind=1, accepted=True)[:30]
        settings = models.Setting.objects.get()
        feedback = request.session.pop('feedback') if 'feedback' in request.session else False
        lessons = settings.main_marathon.lesson_set.all().order_by('number')
        lessons_1 = lessons[:math.floor(len(lessons) / 2)]
        lessons_2 = lessons[math.ceil(len(lessons) / 2):]
        context = self.make_context(form=form,
                                    reviews=reviews,
                                    settings=settings,
                                    feedback=feedback,
                                    lessons_1=lessons_1,
                                    lessons_2=lessons_2,
                                    GOOGLE_RECAPTCHA_SITE_KEY=cnf.RECAPTCHA_PUBLIC_KEY)
        return render(request, 'index.html', context=context)

    def get(self, request, form=None):
        return self.base(request, form)

    def post(self, request):
        form = forms.Feedback(request.POST)
        if form.is_valid():
            fields = {'firstname': 'Имя', 'contact': 'Контакты', 'message': 'Сообщение'}
            message = ''
            for k, v in form.cleaned_data.items():
                if k != 'captcha':
                    message += f'{fields.get(k)}: "{v}"\n'
            subject = 'Новое сообщение по обратной связи  марафона "Движение Вверх"'
            settings = models.Setting.objects.filter().first()
            if not settings:
                form.errors['custom'] = f"При отправке сообщения произошла ошибка. Повторите попытку позднее."
                return self.base(request, form)
            email = settings.contact_mail
            send_email = models.sendmail(subject=subject, message=message, recipient_list=[email], )
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
            email = (form.cleaned_data.get("email")).strip().lower()
            ageconfirm = form.cleaned_data.get("ageconfirm")
            if not ageconfirm:
                form.errors['ageconfirm'] = "Этот флажок должен быть установлен"
            else:
                # user, new = models.User.objects.get_or_create(username__iexact=email)
                user_exists = models.User.objects.filter(username__iexact=email).exists()
                if user_exists:
                    form.errors['custom'] = f"Пользователь с почтой {email} уже зарегистрирован"
                else:
                    user = models.User.objects.create(username=email,
                                                      first_name=firstname,
                                                      last_name=lastname,
                                                      email=email
                                                      )
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
                                        "settings": settings,
                                        "account": account}
                        html_message = render_to_string('mail/registration.html', mail_context)
                        # plain_message = strip_tags(html_message)
                        send_email = models.sendmail(subject=subject, message=html_message, recipient_list=[email])
                        if not send_email:
                            account.registry_sent = False
                            account.save()
                        else:
                            account.registry_sent = True
                            account.save()
                            request.session[
                                'registry'] = f'Данные для входа в личный кабинет отправлены на <span class="text-primary">{email}</span>'
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
            username = (form.cleaned_data.get("login")).strip().lower()
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
    def post(self, request):
        if models.Account.objects.filter(user=self.request.user).exists():
            if request.POST.get('method') == "check" and self.request.user.account.payment_set.exists():
                return JsonResponse({"payments": True})
            subject = 'Удаление профиля на платформе марафона "Движение Вверх"'
            settings = models.Setting.objects.filter().first()
            mail_context = {"login": self.request.user.email,
                            "settings": settings}
            html_message = render_to_string('mail/remove.html', mail_context)
            # plain_message = strip_tags(html_message)
            send_email = models.sendmail(subject=subject, message=html_message,
                                         recipient_list=[self.request.user.email])
            if not send_email:
                return JsonResponse({'sendmail': send_email})
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
            email = (form.cleaned_data['email']).strip().lower()
            account = models.Account.objects.filter(user__email__iexact=email).first()
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
                    send_email = models.sendmail(subject=subject, message=html_message, recipient_list=email)
                    if not send_email:
                        form.errors['custom'] = "Ошибка при сбросе пароля. Повторите попытку позднее."
                    else:
                        form_html = get_template('includes/reset_redirect.html').render(context={'email': email},
                                                                                        request=request)
                        context = self.make_context(form_html=form_html, title='Сброс пароля')
                        return render(request, "auth.html", context)
        return self.base(request, form=form)


class Account(LoginRequiredMixin, ContextViewMixin):

    @staticmethod
    def values2dict(values: iter, key: str, many: bool = True):
        values_dict = {}
        if many:
            for item in values:
                if item[key] in values_dict:
                    values_dict[item[key]].append(item)
                else:
                    values_dict[item[key]] = [item]
        else:
            for item in values:
                values_dict[item[key]] = item
        return values_dict

    def get(self, request):
        if not models.Account.objects.filter(user=self.request.user).exists():
            return HttpResponseRedirect('/')
        context = {}
        account: models.Account = request.user.account
        marathon = request.GET.get('marathon')
        marathon = models.Marathon.objects.filter(pk=marathon, outdated=False).first()
        # marathones = models.Marathon.objects.filter(lesson__payment__account=account).distinct()
        marathones = models.Marathon.objects.filter(outdated=False).distinct()
        if marathones.count() == 1 and marathon is None:
            marathon = models.Marathon.objects.filter(outdated=False).first()
        if marathon:
            lessons = models.Lesson.objects.filter(marathon=marathon).order_by('number')
            payments = models.Payment.objects.filter(account=account, marathon=marathon)
            if payments:
                # есть ли актуальный (не просроченный) платеж за марафон
                payment_valid = payments.filter(date_approve__gte=datetime.now() - timedelta(days=62)).order_by(
                    '-date_pay').first()
                # есть ли просроченный платеж за марафон
                payment_expired = payments.filter(date_approve__lt=datetime.now() - timedelta(days=62)).order_by(
                    '-date_pay').first()

                context = self.make_context(payment_valid=payment_valid, payment_expired=payment_expired)

        else:
            lessons = []
        form = forms.Review()
        context = self.make_context(context=context, marathon=marathon, marathones=marathones, lessons=lessons,
                                    form=form)
        return render(request, 'account_ready.html', context=context)

    def post(self, request):
        """ для отзывов """
        if not models.Account.objects.filter(user=self.request.user).exists():
            return HttpResponseRedirect('/')
        form = forms.Review(request.POST, files=request.FILES)
        if form.is_valid():
            photo = form.cleaned_data.get("photo")
            review = form.cleaned_data["review"]
            kind = models.ReviewKind.objects.filter(pk=1).first()
            account = self.request.user.account
            account.photo = photo
            account.save()
            img = Image.open(account.photo.path)

            # exif = dict(pilImage._getexif().items())
            orientation = 0
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif and orientation in exif:
                if exif[orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)

            if img.width > img.height:
                delta_crop = (img.width - img.height) / 2
                img = img.crop((delta_crop, 0, img.width - delta_crop, img.height))
            elif img.height > img.width:
                delta_crop = (img.height - img.width) / 2
                img = img.crop((0, delta_crop, img.width, img.height - delta_crop))
            if img.width > 300 or img.height > 300:
                img = img.resize((300, 300))
            img.save(account.photo.path, quality=80)
            review_obj = models.Feedback.objects.create(account=account, feedback=review, kind=kind)
            settings = models.Setting.objects.filter().first()
            subject = 'НОВЫЙ ОТЗЫВ О МАРАФОНЕ'
            message = f'<p>Пользователь: {account.user.get_username} - {account.user.email} </p>' \
                      f'<p>Текст отзыва: "{review_obj.feedback}" </p>' \
                      f'<a style="font-size: 24px; font-weight: bold;" href="{settings.website}/api/accept_review/{account.pk}-{review_obj.pk}">Опубликовать отзыв</a>'
            mail_context = {"settings": settings, "message": message}
            html_message = render_to_string('mail/news.html', mail_context)
            models.sendmail(subject, html_message, settings.contact_mail, attach=review_obj.account.photo.path)

        return HttpResponseRedirect('/me')


class Book(ContextViewMixin):
    def base(self, request):
        reviews = models.Feedback.objects.filter(kind=2, accepted=True)
        context = self.make_context(reviews=reviews)
        return render(request, 'book.html', context=context)

    def get(self, request):
        return self.base(request)


class VideoLooked(LoginRequiredMixin, ContextViewMixin):
    def post(self, request):
        res = {}
        account = models.Account.objects.filter(user=self.request.user).first()
        if account:
            video_pk = request.POST.get('video')
            video = models.Video.objects.filter(pk=video_pk).first()
            if video and not video in account.looked_videos.filter(pk=video_pk):
                account.looked_videos.add(video)
                res['result'] = 'success'
                try:
                    videos_l = set(video.lesson.video_set.values_list('pk', flat=True))
                    videos_a = set(
                        account.looked_videos.filter(lesson__pk=video.lesson.pk).values_list('pk', flat=True))
                    if videos_l == videos_a:
                        res['lesson'] = video.lesson.pk

                        lesson_next = video.lesson.next()
                        context = self.make_context(lesson=lesson_next)
                        payments = models.Payment.objects.filter(account=account, marathon=video.lesson.marathon)
                        if payments:
                            # есть ли актуальный (не просроченный) платеж за марафон
                            payment_valid = payments.filter(
                                date_approve__gte=datetime.now() - timedelta(days=62)).order_by(
                                '-date_pay').first()
                            # есть ли просроченный платеж за марафон
                            payment_expired = payments.filter(
                                date_approve__lt=datetime.now() - timedelta(days=62)).order_by(
                                '-date_pay').first()

                            context.update({"payment_valid": payment_valid, "payment_expired": payment_expired})
                        html_title = get_template('includes/lesson_title.html').render(context, request=request)
                        # html_body = get_template('includes/lesson_body.html').render(context, request=request)
                        # res.update(
                        #     {"html_title": html_title, "html_body": html_body, 'lesson_next': lesson_next.number or None})
                        res.update(
                            {"html_title": html_title, 'lesson_next': lesson_next.number or None})
                except:
                    pass
        else:
            res['result'] = 'error'
        return JsonResponse(res)
