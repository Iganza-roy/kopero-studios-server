# Generated by Django 5.1.1 on 2024-10-14 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kopero_auth', '0002_profile_description_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='picture',
            field=models.URLField(blank=True),
        ),
    ]
