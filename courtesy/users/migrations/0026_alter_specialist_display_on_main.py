# Generated by Django 4.2.1 on 2025-01-06 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_specialist_display_on_main_alter_news_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialist',
            name='display_on_main',
            field=models.BooleanField(default=False, verbose_name='Отображать на главной странице'),
        ),
    ]
