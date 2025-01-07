from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path('login/', views.login_view, name='login'),
    path('personal/', views.personal_view, name='personal'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),  # Выход
    path("about/", views.about, name='about'),
    path('addresses/', views.addresses_view, name='addresses'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('doctors/', views.specialists_view, name='specialists'),
    path('services/', views.service_list_view, name='services'),
    path('news/', views.news_list_view, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),

]
