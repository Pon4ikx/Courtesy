from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import courtesy.constant as const


# Create your views here.


def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def personal_view(request):
    # Проверяем, авторизован ли пользователь
    if not request.user.is_authenticated:
        return redirect('login')  # Имя маршрута логина
    return render(request, 'personal.html')  # Рендер личного кабинета


# Страница входа
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email == const.ADMIN_NAME and password == const.ADMIN_PASSWORD:
            # Здесь вы можете установить пользователя как администратора
            return redirect('admin')  # Имя маршрута для страницы admin.html

        # Если учетные данные неверные, вы можете добавить сообщение об ошибке
        context = {'error': 'Неверная электронная почта или пароль.'}
        return render(request, 'login.html', context)

    return render(request, 'login.html')


# Страница регистрации
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def get_days_in_month(year, month):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        return 29 if is_leap_year(year) else 28
    return 0


def signup_view(request):
    years = list(range(1940, 2024))
    months = list(range(1, 13))

    # По умолчанию, значение дня пустое
    days = []

    if request.method == 'POST':
        selected_year = int(request.POST.get('birth-year', 1900))
        selected_month = int(request.POST.get('birth-month', 1))
        days_count = get_days_in_month(selected_year, selected_month)
        days = list(range(1, days_count + 1))
    else:
        # Если это первый запрос, показываем пустой список дней
        days = list(range(1, 32))  # По умолчанию для отображения

    context = {
        'years': years,
        'months': months,
        'days': days,
    }

    return render(request, 'signup.html', context)
