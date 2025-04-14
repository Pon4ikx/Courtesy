from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from django.contrib.auth import logout
from random import sample
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Specialist, News, Address, Contacts, Category, Service, Review, Account, EmailConfirmationCode
from .serializers import AdressSerializer
import random
from .utils import send_confirmation_email


def index(request):
    specialists_to_display = Specialist.objects.filter(display_on_main=True)

    # Получаем случайных 3 специалистов, если их больше 3
    if specialists_to_display.count() > 3:
        specialists = sample(list(specialists_to_display), 3)
    else:
        specialists = specialists_to_display
    news_list = News.objects.all()[:4]

    context = {
        'specialists': specialists,
        'news_list': news_list,
    }

    return render(request, 'index.html', context)


def about(request):
    return render(request, "about.html")


def logout_view(request):
    logout(request)
    return redirect('login')


# Страница входа
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('personal')
        else:
            return render(request, 'login.html', {'error': 'Неправильный email или пароль.'})

    return render(request, 'login.html')


# Личный кабинет
@login_required
def personal_view(request):
    return render(request, 'personal.html')  # Рендер личного кабинета


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя, но не активируем его сразу
            user = form.save(commit=False)
            user.is_active = False  # Блокируем до подтверждения email
            user.save()

            # Генерация кода подтверждения
            code = str(random.randint(100000, 999999))  # Генерация случайного 6-значного кода
            # Сохраняем код подтверждения в базе данных
            EmailConfirmationCode.objects.create(user=user, code=code)

            # Отправка письма с кодом подтверждения
            send_confirmation_email(user, code)

            return redirect('confirm_email')  # Редирект на страницу подтверждения (нужно создать эту страницу)
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def confirm_email(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            confirmation = EmailConfirmationCode.objects.get(code=code)
            user = confirmation.user
            user.is_active = True
            user.save()
            confirmation.delete()
            return redirect('login')  # или куда надо
        except EmailConfirmationCode.DoesNotExist:
            return render(request, 'confirm_email.html', {'error': 'Неверный код'})
    return render(request, 'confirm_email.html')


def resend_email(request):
    if request.method == 'POST':
        # Получаем email пользователя
        email = request.POST.get('email')
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return render(request, 'confirm_email.html', {'error': 'Пользователь с таким email не найден'})

        # Генерация нового кода
        code = str(random.randint(100000, 999999))
        EmailConfirmationCode.objects.create(user=user, code=code)

        # Отправка нового кода
        send_confirmation_email(user, code)

        # Возвращаем ту же страницу с сообщением
        return render(request, 'confirm_email.html', {
            'message': 'Код подтверждения был отправлен на ваш email!',
        })

    # Если запрос GET, просто отображаем страницу
    return render(request, 'confirm_email.html')


def specialists_view(request):
    categories = Category.objects.all()

    selected_categories = request.GET.getlist('categories')
    if selected_categories:
        specialists = Specialist.objects.filter(category__id__in=selected_categories)
    else:
        specialists = Specialist.objects.all()

    return render(request, 'specialists.html', {
        'specialists': specialists,
        'categories': categories,
        'selected_categories': selected_categories
    })


def news_list_view(request):
    news = News.objects.all()
    return render(request, 'news.html', {'news': news})


def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)
    return render(request, 'news_detail.html', {'news': news})


def addresses_view(request):
    addresses = Address.objects.all()
    return render(request, 'addresses.html', {'addresses': addresses})


def contacts_view(request):
    contacts = Contacts.objects.all()
    return render(request, 'contacts.html', {'contacts': contacts})


def service_list_view(request):
    categories = Category.objects.all()

    selected_categories = request.GET.getlist('categories')
    if selected_categories:
        services = Service.objects.filter(category__id__in=selected_categories)
    else:
        services = Service.objects.all()

    return render(request, 'services.html', {
        'services': services,
        'categories': categories
    })


def reviews_view(request):
    reviews = Review.objects.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    return render(request, 'reviews.html', {'reviews': reviews, 'average_rating': average_rating})


class AdressesViewSet(ReadOnlyModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AdressSerializer
