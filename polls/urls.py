from django.urls import path
from . import views


app_name = "polls"
urlpatterns = [
    path('error/', views.error_view, name='error'),
    path('login/', views.login_view, name='login'),
    path('xss_vulnerable/', views.xss_vulnerable_view, name='xss_vulnerable'),
    path('vulnerable_view/', views.vulnerable_view, name='vulnerable_view'),
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]