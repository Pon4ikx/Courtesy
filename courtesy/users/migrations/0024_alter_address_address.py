# Generated by Django 4.2.1 on 2025-01-04 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_contacts_what_doing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='address',
            field=models.CharField(help_text='Пример: ул. (Название улицы или проспекта(пр.)), (Номер дома), Город\n', max_length=255, unique=True, verbose_name='Адрес'),
        ),
    ]
