# Generated by Django 4.2.1 on 2024-12-28 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Specialist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=40, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=40, verbose_name='Имя')),
                ('middle_name', models.CharField(blank=True, max_length=40, null=True, verbose_name='Отчество')),
                ('speciality', models.CharField(max_length=200, verbose_name='Специальность')),
                ('dop_info', models.CharField(blank=True, max_length=200, verbose_name='Специальность')),
            ],
        ),
    ]
