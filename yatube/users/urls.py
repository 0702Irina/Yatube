from django.contrib.auth.views import (
    LogoutView, LoginView,
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView)
from django.urls import path
from users import views


app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='users/password_change_form.html'),
        name='password_change'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'),
        name='password_change/done'
    ),
    path(
        'password_reset',
        PasswordResetView.as_view(
            template_name='users/password_reset_form.html'),
        name='password_reset'
    ),
    path(
        'password_reset/done',
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'),
        name='password_reset/done'
    ),
    path(
        'reset/<uidb64>/<token',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confim.html'),
        name='reset/<uidb64>/<token'
    ),
    path(
        'password/reset/done',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'),
        name='password/reset/done'
    ),
]
