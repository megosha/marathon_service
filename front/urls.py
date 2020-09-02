from django.urls import re_path, path, include

from front import views

urlpatterns = [
    path('', views.Index.as_view()),
]

