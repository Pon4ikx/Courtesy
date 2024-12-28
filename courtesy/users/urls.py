from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.index),
    path('login/', views.login_view, name='login'),
    path('personal/', views.personal_view, name='personal'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),  # Выход
    path("about/", views.about),
]
