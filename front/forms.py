from django_recaptcha.fields import ReCaptchaField
# from captcha.widgets import ReCaptchaV3
from django import forms
from django.core.validators import FileExtensionValidator


class RegisterAccount(forms.Form):
    firstname = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'type': 'text', 'placeholder': 'Имя', "class": "form-control text-multiple"}))
    lastname = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'type': 'text', 'placeholder': 'Фамилия', "class": "form-control text-multiple"}))
    phone = forms.CharField(max_length=18, required=True, widget=forms.TextInput(
        attrs={'type': 'tel', 'placeholder': 'Телефон', "class": "form-control text-multiple",
               'oninput': 'valid_phone(this.id)'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'placeholder': 'Email', "class": "form-control text-multiple", }))
    ageconfirm = forms.BooleanField(required=True, widget=forms.CheckboxInput(
        attrs={'type': 'checkbox', "class": "form-check-input display-7"}))
    captcha = ReCaptchaField()


class Login(forms.Form):
    login = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'placeholder': 'Логин', "class": "form-control input display-7", }))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'type': 'password', 'placeholder': 'Пароль', "class": "form-control display-7"}))
    captcha = ReCaptchaField()


class ResetPWD(forms.Form):
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(
                                 attrs={"class": "form-control input display-7", 'placeholder': 'E-mail'}))
    captcha = ReCaptchaField()


class Feedback(forms.Form):
    """ обратная связь (не отзыв) """
    firstname = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'type': 'text', 'placeholder': 'Ваше имя', "class": "form-control display-7"}))
    contact = forms.CharField(required=True, max_length=50, widget=forms.TextInput(
        attrs={'type': 'text', 'placeholder': 'Ваш телефон или e-mail', "class": "form-control display-7",
               'oninput': 'valid_contact(this.id)'}))
    message = forms.CharField(required=True, max_length=1204, widget=forms.Textarea(
        attrs={'type': 'text', 'placeholder': 'Ваш вопрос или сообщение', "class": "form-control display-7",
               "rows": "2"}))
    captcha = ReCaptchaField()


class Review(forms.Form):
    photo = forms.ImageField(required=False,
                            widget=forms.FileInput(attrs={"accept": '.jpg,.jpeg', "class": "form-control display-7"}),
                            validators=[FileExtensionValidator(['jpg', 'jpeg'])])
    review = forms.CharField(required=True, max_length=1204, widget=forms.Textarea(
        attrs={'type': 'text', 'placeholder': 'Ваш отзыв', "class": "form-control display-7",
               "rows": "6"}))
