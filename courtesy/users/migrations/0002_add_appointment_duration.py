from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialist',
            name='appointment_duration',
            field=models.PositiveIntegerField(
                default=20,
                verbose_name='Длительность приёма (в минутах)'
            ),
        ),
    ]
