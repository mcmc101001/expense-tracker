from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

# Create your models here.

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    budget = models.IntegerField(default=0)
    constant_reminder = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

class Expense(models.Model):
    TYPES = (
        ('Meals', 'Meals'),
        ('Snacks', 'Snacks'),
        ('Gifts', 'Gifts'),
        ('Clothes', 'Clothes'),
        ('Transport', 'Transport'),
        ('Entertainment', 'Entertainment'),
        ("Won't use but still buy", "Won't use but still bye"),
        ('Misc.', 'Misc.')
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPES)
    datetime = models.DateTimeField(default= timezone.now)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    user = models.ForeignKey(CustomUser, related_name='expenses', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name