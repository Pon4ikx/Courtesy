from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, BookingForm, UserProfileForm, ReviewForm
from django.contrib.auth import logout
from random import sample
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Specialist, News, Address, Contacts, Category, Service, Review, Account, EmailConfirmationCode, \
    Cabinet, SpecialistService, Talon, Schedule
from .serializers import AdressSerializer
import random
from .utils import send_confirmation_email
from django.http import JsonResponse
from datetime import timedelta, datetime
from django.contrib import messages
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.utils import timezone


def global_search(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return render(request, 'search_results.html', {'empty_query': True})

    from .models import Specialist, Service

    # Поиск специалистов
    specialists = Specialist.objects.annotate(
        full_name=Concat(
            'last_name', Value(' '),
            'first_name', Value(' '),
            'middle_name',
            output_field=CharField()
        )
    ).filter(
        Q(full_name__icontains=query) |
        Q(category__name__icontains=query) |
        Q(speciality__icontains=query)
    ).distinct()

    # Поиск услуг
    services = Service.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )

    return render(request, 'search_results.html', {
        'query': query,
        'specialists': specialists[:10],  # Ограничиваем количество результатов
        'services': services[:10],
        'has_results': specialists.exists() or services.exists()
    })


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


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
        else:
            messages.error(request, 'Ошибка при обновлении профиля')
    return redirect('personal')


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Ваш аккаунт был успешно удален')
        return redirect('home')
    return redirect('personal')


@login_required
def cancel_talon(request, talon_id):
    if request.method == 'POST':
        try:
            talon = Talon.objects.get(id=talon_id, user=request.user)
            talon.delete()

            # Для AJAX-запросов
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Запись успешно отменена!',
                    'talon_id': talon_id
                })
            # Для обычных запросов
            messages.success(request, 'Запись успешно отменена!')
            return redirect('personal')

        except Talon.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Запись не найдена или уже отменена'
            }, status=404)

    return JsonResponse({
        'status': 'error',
        'message': 'Неправильный метод запроса'
    }, status=400)


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
    # Получаем текущего пользователя
    user = request.user

    # Получаем актуальные талоны (дата >= сегодня)
    current_talons = Talon.objects.filter(
        user=user,
        date__gte=timezone.now().date()
    ).order_by('date', 'time')

    # Получаем историю посещений (дата < сегодня)
    past_talons = Talon.objects.filter(
        user=user,
        date__lt=timezone.now().date()
    ).order_by('-date', '-time')

    user_has_review = Review.objects.filter(user=request.user).exists()

    # Подготавливаем данные для формы
    if request.method == 'POST':
        # Обработка сохранения данных профиля
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Можно добавить сообщение об успешном сохранении
    else:
        form = UserProfileForm(instance=user)

    context = {
        'user': user,
        'current_talons': current_talons,
        'past_talons': past_talons,
        'form': form,
        'user_has_review': user_has_review,
    }

    return render(request, 'personal.html', context)


@login_required
def create_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.date = timezone.localdate()  # Устанавливаем текущую дату
            if 1 <= review.rating <= 5:
                review.save()
                request.user.has_review = True
                request.user.save()
                messages.success(request, 'Спасибо за ваш отзыв!')
                return redirect('personal')
            else:
                form.add_error('rating', 'Оценка должна быть от 1 до 5')
    else:
        form = ReviewForm()

    return render(request, 'create_review.html', {'form': form})


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
    user = request.user if request.user.is_authenticated else None

    if request.method == 'POST':
        if 'resend' in request.POST:
            if user:
                code = str(random.randint(100000, 999999))
                EmailConfirmationCode.objects.filter(user=user).delete()
                EmailConfirmationCode.objects.create(user=user, code=code)
                send_confirmation_email(user, code)
                return render(request, 'confirm_email.html', {'message': 'Код отправлен повторно.'})
        else:
            code = request.POST.get('code')
            confirmation = EmailConfirmationCode.objects.filter(code=code).first()

            if confirmation and confirmation.user:
                confirmation.user.is_active = True
                confirmation.user.save()
                confirmation.delete()
                return redirect('login')
            else:
                return render(request, 'confirm_email.html', {'error': 'Неверный код.'})

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


def specialist_info(request, slug):
    specialist = get_object_or_404(Specialist, slug=slug)
    services = [ss.service for ss in specialist.services.select_related('service').all()]
    return render(request, 'specialist_info.html', {'specialist': specialist, 'services': services})


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


def get_services_for_specialist(request):
    specialist_id = request.GET.get('specialist_id')
    services = []
    if specialist_id:
        links = SpecialistService.objects.filter(specialist_id=specialist_id).select_related('service')
        services = [{'id': link.service.id, 'name': link.service.name} for link in links]
    return JsonResponse({'services': services})


def get_specialists_for_service(request):
    service_id = request.GET.get('service_id')
    specialists = []
    if service_id:
        links = SpecialistService.objects.filter(service_id=service_id).select_related('specialist')
        specialists = [{
            'id': link.specialist.id,
            'last_name': link.specialist.last_name,
            'first_name': link.specialist.first_name,
            'middle_name': link.specialist.middle_name
        } for link in links]
    return JsonResponse({'specialists': specialists})


def booking_view(request):
    specialist_id = request.GET.get('specialist')
    service_id = request.GET.get('service')

    selected_specialist = Specialist.objects.filter(id=specialist_id).first() if specialist_id else None
    selected_service = Service.objects.filter(id=service_id).first() if service_id else None

    form = BookingForm(
        request.POST or None,
        fixed_specialist=selected_specialist,
        fixed_service=selected_service
    )

    available_talons = []
    selected_date = None

    if form.is_valid():
        selected_date = form.cleaned_data.get("date")
        specialist = form.cleaned_data["specialist"]

        # Получаем расписание специалиста на выбранную дату
        schedule = Schedule.objects.filter(specialist=specialist, date=selected_date).first()

        if schedule:
            start = datetime.combine(selected_date, schedule.start_time)
            end = datetime.combine(selected_date, schedule.end_time)
            duration = timedelta(minutes=specialist.appointment_duration)

            # Получаем все занятые талоны на эту дату и специалиста
            booked_talons = Talon.objects.filter(
                doctor=specialist,
                date=selected_date
            ).values_list('time', flat=True)  # Получаем список занятых времён

            current = start
            available_talons = []

            while current + duration <= end:
                time_slot = current.time()

                # Добавляем только свободные талоны
                if time_slot not in booked_talons:
                    available_talons.append(time_slot)

                current += duration

    return render(request, 'booking.html', {
        'form': form,
        'selected_specialist': selected_specialist,
        'selected_service': selected_service,
        'available_talons': available_talons,
        'selected_date': selected_date,
    })


@login_required
def create_talon(request):
    if request.method == 'POST':
        specialist_id = request.POST.get('specialist_id')
        service_id = request.POST.get('service_id')
        date = request.POST.get('date')
        time = request.POST.get('time')
        dop_info = request.POST.get('dop_info', '')

        if Talon.objects.filter(doctor_id=specialist_id, date=date, time=time).exists():
            messages.error(request, 'Это время уже занято! Пожалуйста, выберите другое время.')
            return redirect('booking')

        specialist = Specialist.objects.get(id=specialist_id)
        service = Service.objects.get(id=service_id)

        # Получаем кабинет из расписания
        schedule = Schedule.objects.filter(specialist=specialist, date=date).first()
        cabinet = schedule.cabinet if schedule else "Кабинет не указан"

        Talon.objects.create(
            user=request.user,
            date=date,
            time=time,
            doctor=specialist,
            service=service,
            cabinet=cabinet,
            dop_info=dop_info  # Сохраняем дополнительную информацию
        )

        messages.success(request, 'Запись успешно создана!')
        return redirect('personal')

    return redirect('booking')
