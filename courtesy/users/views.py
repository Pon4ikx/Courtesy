from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from django.contrib.auth import logout
from django.utils.timezone import now
from .models import Specialist, News, Address, Contacts, Category


# Create your views here.


def index(request):
    # Получаем первых 3 специалистов
    specialists = Specialist.objects.all()[:3]

    # Получаем последние 3 новости, сортированные по дате публикации
    news_list = News.objects.all()[:4]

    # Добавляем данные в контекст
    context = {
        'specialists': specialists,
        'news_list': news_list,
    }

    return render(request, 'index.html', context)


def about(request):
    return render(request, "about.html")


def logout_view(request):
    logout(request)
    return redirect('login')  # Перенаправление на страницу входа


# Страница входа
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Аутентификация пользователя через кастомный бэкенд
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)  # Вход пользователя
            return redirect('personal')  # Перенаправление на личный кабинет
        else:
            # Возврат на страницу входа с ошибкой
            return render(request, 'login.html', {'error': 'Неправильный email или пароль.'})

    return render(request, 'login.html')  # GET-запрос (отображение страницы входа)


# Личный кабинет
@login_required
def personal_view(request):
    return render(request, 'personal.html')  # Рендер личного кабинета


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Перенаправление на страницу входа
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def specialists_view(request):
    # Получение всех категорий
    categories = Category.objects.all()

    # Получение списка категорий, выбранных для фильтрации
    selected_categories = request.GET.getlist('categories')

    # Фильтрация специалистов по выбранным категориям
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
    news_list = News.objects.all()
    return render(request, 'news_list.html', {'news_list': news_list, 'now': now()})


def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)
    return render(request, 'news_detail.html', {'news': news})


def addresses_view(request):
    addresses = Address.objects.all()
    return render(request, 'addresses.html', {'addresses': addresses})


def contacts_view(request):
    contacts = Contacts.objects.all()
    return render(request, 'contacts.html', {'contacts': contacts})