from django.urls import path

from front import views, api

urlpatterns = [
    path('', views.Index.as_view()),
    path('me', views.Account.as_view()),
    path('register', views.Register.as_view()),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view()),
    path('remove', views.RemoveAccount.as_view()),
    path('reset', views.ResetPassword.as_view()),
    path('api/account_deny/<str:uuid>_<str:login>', api.AccountDeny.as_view()),
    path('accountdeny', api.RenderDeny.as_view()),
    path('book', views.Book.as_view()),
    path('get_invoice/<str:filename>', views.get_invoice),
    path('get_hometask/<int:marathon_pk>-<int:lesson_number>', views.get_hometask),
    path('api/accept_review/<str:account_id>-<int:feedback_id>', api.AcceptReview.as_view()),
    path('video-looked', views.VideoLooked.as_view()),
    path('get_gift/<str:marathon>', views.get_gift),

    # path('test', views.Test.as_view()),
]

