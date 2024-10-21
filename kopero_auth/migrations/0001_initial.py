# Generated by Django 5.1.1 on 2024-10-21 09:59

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, unique=True, verbose_name='email address')),
                ('username', models.CharField(blank=True, max_length=150, unique=True, verbose_name='username')),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('bio', models.TextField(blank=True, max_length=1000)),
                ('is_ops_admin', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. ', verbose_name='active')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether this user is staff or not. ', verbose_name='staff')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('baseuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('bookings', models.JSONField(blank=True, default=list, null=True)),
            ],
            options={
                'db_table': 'clients',
                'ordering': ['-date_joined'],
            },
            bases=('kopero_auth.baseuser',),
        ),
        migrations.CreateModel(
            name='CrewMember',
            fields=[
                ('baseuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('category', models.CharField(choices=[('photographer', 'Photographer'), ('videographer', 'Videographer')], max_length=50)),
                ('sessions_booked', models.JSONField(blank=True, default=list, null=True)),
            ],
            options={
                'db_table': 'crew',
                'ordering': ['-date_joined'],
            },
            bases=('kopero_auth.baseuser',),
        ),
    ]
