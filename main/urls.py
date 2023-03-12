from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.index, name="index"),
    # authentication
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('expense_list', views.expense_list, name="expense_list"),
    path('delete_expense', views.delete_expense, name="delete_expense"),
]
