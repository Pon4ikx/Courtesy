# users/migrations/0003_schedule_and_cabinet.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_appointment_duration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cabinet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10, unique=True, verbose_name='Номер кабинета')),
                ('category', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='users.category',
                    verbose_name='Направление'
                )),
            ],
            options={
                'verbose_name': 'Кабинет',
                'verbose_name_plural': 'Кабинеты',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата')),
                ('start_time', models.TimeField(verbose_name='Время начала')),
                ('end_time', models.TimeField(verbose_name='Время окончания')),
                ('is_day_off', models.BooleanField(default=False, verbose_name='Выходной')),
                ('cabinet', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='users.cabinet',
                    verbose_name='Кабинет'
                )),
                ('specialist', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='users.specialist',
                    verbose_name='Специалист'
                )),
            ],
            options={
                'verbose_name': 'Расписание',
                'verbose_name_plural': 'Расписания',
                'unique_together': {('specialist', 'date')},
            },
        ),
    ]
