from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Value, Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from zoneinfo import ZoneInfo
from datetime import datetime

from .models import CustomUser, Expense

# Create your views here.
@login_required(login_url='/main/login')
def index(request):
    return render(request, "main/index.html")

### LIST MODULE ###
@login_required(login_url='/main/login')
def expense_list(request):
    now = datetime.now(ZoneInfo('Asia/Singapore'))
    current_user = CustomUser.objects.get(user=request.user)
    expenses = Expense.objects.filter(user=current_user).exclude(datetime__month=now.month, datetime__year=now.year).order_by("-datetime")
    expenses_current_month = Expense.objects.filter(user=current_user, datetime__month=now.month, datetime__year=now.year).exclude(datetime__day=now.day).order_by("-datetime")
    expenses_current_day = Expense.objects.filter(user=current_user, datetime__day=now.day, datetime__month=now.month, datetime__year=now.year).order_by("-datetime")
    cost = expenses.aggregate(total=Sum("cost"))['total']
    cost_month = expenses_current_month.aggregate(total=Sum("cost"))['total']
    cost_day = expenses_current_day.aggregate(total=Sum("cost"))['total']
    budget = current_user.budget
    remaining_budget = budget
    if cost:
        cost = round(float(cost), 2)
    if cost_month:
        cost_month = round(float(cost_month), 2)
        remaining_budget -= cost_month
    if cost_day:
        cost_day = round(float(cost_day), 2)
        remaining_budget -= cost_day
    return render(request, "main/expense_list.html", {
        "cost": cost,
        "cost_month": cost_month,
        "cost_day": cost_day,
        "expenses": expenses,
        "expenses_month": expenses_current_month,
        "expenses_day": expenses_current_day,
        "budget": budget,
        "remaining_budget": remaining_budget
    })    

# TO-DO #
def delete_expense(request):
    return HttpResponseRedirect(reverse('main:expense_list'))

### AUTHENTICATION MODULE ###
# logging in and out
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("main:index"))
        else:
            return render(request, 'main/login.html', {
                "message": "Incorrect username or password"
            })
    return render(request, 'main/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'main/login.html', {
        "message": "Logged out successfully"
    })
    