from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views
from .views import AdressesViewSet
from django.contrib.auth import views as auth_views

router = SimpleRouter()
router.register('api/addresses', AdressesViewSet)

urlpatterns = [
                  path("", views.index, name='home'),
                  path('login/', views.login_view, name='login'),
                  path('personal/', views.personal_view, name='personal'),
                  path('signup/', views.signup_view, name='signup'),
                  path('logout/', views.logout_view, name='logout'),

                  path('update-profile/', views.update_profile, name='update_profile'),
                  path('delete-account/', views.delete_account, name='delete_account'),
                  path('password-change/',
                       auth_views.PasswordChangeView.as_view(
                           template_name='password_change.html',
                           success_url='/personal/'
                       ),
                       name='password_change'),
                  path('cancel_talon/<int:talon_id>/', views.cancel_talon, name='cancel_talon'),

                  path("about/", views.about, name='about'),
                  path('addresses/', views.addresses_view, name='addresses'),
                  path('contacts/', views.contacts_view, name='contacts'),
                  path('doctors/', views.specialists_view, name='specialists'),
                  path('services/', views.service_list_view, name='services'),
                  path('news/', views.news_list_view, name='news_list'),
                  path('news/<slug:slug>/', views.news_detail, name='news_detail'),

                  path('reviews/', views.reviews_view, name='reviews_list'),
                  path('reviews/create/', views.create_review, name='create_review'),

                  path('confirm_email/', views.confirm_email, name='confirm_email'),
                  path('specialist/<slug:slug>/', views.specialist_info, name='specialist_info'),

                  path('booking/', views.booking_view, name='booking'),
                  path('ajax/get_services/', views.get_services_for_specialist, name='get_services_for_specialist'),
                  path('ajax/get_specialists/', views.get_specialists_for_service, name='get_specialists_for_service'),
                  path('create-talon/', views.create_talon, name='create_talon'),

                  path('search/', views.global_search, name='global_search'),

              ] + router.urls
