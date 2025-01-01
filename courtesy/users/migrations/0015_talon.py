# Generated by Django 4.2.1 on 2025-01-01 16:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_news'),
    ]

    operations = [
        migrations.CreateModel(
            name='Talon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата приёма')),
                ('cabinet', models.CharField(max_length=20, verbose_name='Кабинет')),
                ('time', models.TimeField(verbose_name='Время приёма')),
                ('dop_info', models.TextField(blank=True, verbose_name='Дополнительная информация')),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='talons', to='users.specialist', verbose_name='Врач')),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='talons', to='users.service', verbose_name='Услуга')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='talons', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Талон',
                'verbose_name_plural': 'Талоны',
            },
        ),
    ]
