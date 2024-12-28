from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from django.contrib.auth import logout


# Create your views here.


def index(request):
    return render(request, "index.html")


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
    return render(request, 'specialists.html')
