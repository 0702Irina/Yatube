# from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm, PasswordResetForm)
# from django.contrib.auth.forms import UsernameField, AuthenticationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ResetForm(PasswordResetForm):
    pass


# class Authentication(AuthenticationForm):
#    username = UsernameField(help_text="Введите имя",
#                             widget=forms.TextInput(
#                       attrs={'autofocus': True}))
#   password = forms.CharField(help_text="введите пароль",
#                              label=("Password"),
#                              strip=False,
#                             widget=forms.PasswordInput,)
