# Generated by Django 4.1.5 on 2023-01-27 15:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_expense_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
