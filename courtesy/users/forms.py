from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account


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
                self.initial[field_name] = ''  # Заменяем None на пустую строку

