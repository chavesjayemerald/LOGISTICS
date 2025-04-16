# Generated by Django 5.1 on 2025-04-15 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, default='single_user', max_length=255, null=True, unique=True)),
                ('password', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('firstname', models.CharField(max_length=55)),
                ('middlename', models.CharField(blank=True, max_length=55, null=True)),
                ('lastname', models.CharField(max_length=55)),
                ('email_address', models.EmailField(blank=True, max_length=255, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=55, null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='custom_user_set', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='custom_user_set', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'tbl_users',
            },
        ),
    ]
