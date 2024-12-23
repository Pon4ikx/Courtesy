from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path('personal/', views.personal_view, name='personal'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path("about/", views.about),
]
