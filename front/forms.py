from django import forms


class RegisterAccount(forms.Form):
    firstname = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'type':'text', 'placeholder': 'Имя', "class": "form-control text-multiple"}))
    lastname = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'type':'text', 'placeholder': 'Фамилия', "class": "form-control text-multiple"}))
    phone = forms.CharField(max_length=18, required=True, widget=forms.TextInput(
        attrs={'type':'tel', 'placeholder': 'Телефон', "class": "form-control text-multiple",
               'oninput':'valid_phone(this.id)'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'placeholder': 'Email', "class": "form-control text-multiple",}))
    ageconfirm = forms.BooleanField(required=True, widget=forms.CheckboxInput(
        attrs={'type':'checkbox', "class": "form-check-input display-7"}))


class Login(forms.Form):
    login = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'placeholder': 'Логин', "class": "form-control input display-7",}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'type': 'password', 'placeholder': 'Пароль', "class": "form-control display-7"}))

class ResetPWD(forms.Form):
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={"class": "form-control input display-7", 'placeholder': 'E-mail'}))
