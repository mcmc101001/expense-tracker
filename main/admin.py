from django.contrib import admin

from .models import CustomUser, Expense

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Expense)