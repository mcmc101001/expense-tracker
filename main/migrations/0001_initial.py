# Generated by Django 4.1.5 on 2023-01-23 08:36

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('budget', models.IntegerField(default=0)),
                ('constant_reminder', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('Meals', 'Meals'), ('Snacks', 'Snacks'), ('Gifts', 'Gifts'), ('Clothes', 'Clothes'), ('Misc.', 'Misc.')], max_length=255)),
                ('datetime', models.DateTimeField(default=datetime.datetime(2023, 1, 23, 16, 36, 40, 736843))),
                ('cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='main.customuser')),
            ],
        ),
    ]
