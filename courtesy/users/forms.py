from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account, Specialist, Service, Review
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Опишите ваш опыт посещения...'
            }),
        }
        labels = {
            'content': 'Текст отзыва'
        }


class SignupForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ['last_name', 'first_name', 'middle_name', 'date_of_birth', 'phone', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот адрес электронной почты уже используется.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.initial.get(field_name) is None:
                self.initial[field_name] = ''


class BookingForm(forms.Form):
    specialist = forms.ModelChoiceField(queryset=Specialist.objects.all(), label="Специалист")
    service = forms.ModelChoiceField(queryset=Service.objects.all(), label="Услуга")
    date = forms.DateField(
        label="Дата",
        widget=forms.DateInput(attrs={"type": "date", "min": datetime.date.today().isoformat()}),
        required=False
    )

    def __init__(self, *args, fixed_specialist=None, fixed_service=None, **kwargs):
        super().__init__(*args, **kwargs)

        if fixed_specialist:
            self.fields['specialist'].queryset = Specialist.objects.filter(id=fixed_specialist.id)
            self.fields['specialist'].initial = fixed_specialist
            self.fields['specialist'].disabled = True
            self.fields['service'].queryset = Service.objects.filter(
                specialists__specialist=fixed_specialist
            )

        if fixed_service:
            self.fields['service'].queryset = Service.objects.filter(id=fixed_service.id)
            self.fields['service'].initial = fixed_service
            self.fields['service'].disabled = True
            self.fields['specialist'].queryset = Specialist.objects.filter(
                services__service=fixed_service
            )


User = get_user_model()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone and len(phone) < 5:
            raise ValidationError("Номер телефона слишком короткий")
        return phone
