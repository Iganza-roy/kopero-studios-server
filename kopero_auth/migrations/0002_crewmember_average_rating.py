# Generated by Django 5.1.1 on 2024-10-22 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kopero_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='crewmember',
            name='average_rating',
            field=models.FloatField(default=0.0),
        ),
    ]
