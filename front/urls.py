from django.urls import re_path, path, include

from front import views

urlpatterns = [
    path('', views.Index.as_view()),
    path('me', views.Account.as_view()),
    path('register', views.Register.as_view()),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view()),
    path('reset', views.ResetPassword.as_view()),
]

