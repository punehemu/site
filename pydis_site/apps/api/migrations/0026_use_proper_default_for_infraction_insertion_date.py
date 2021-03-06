# Generated by Django 2.1.5 on 2019-01-09 19:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_allow_custom_inserted_at_infraction_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infraction',
            name='inserted_at',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='The date and time of the creation of this infraction.'),
        ),
    ]
