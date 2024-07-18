from django.urls import path

from . import views

app_name = "transactions"

urlpatterns = [
    path('', views.dashboard, name="Transaction Dashboard")
]
