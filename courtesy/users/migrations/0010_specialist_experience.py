# Generated by Django 4.2.1 on 2024-12-31 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_specialist_options_remove_category_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialist',
            name='experience',
            field=models.CharField(max_length=25, null=True, verbose_name='Стаж работы'),
        ),
    ]