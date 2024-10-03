from django.urls import path

from . import views

app_name = "transactions"

urlpatterns = [
    path('', views.dashboard, name="transactions"),
    # path('<str:recipient_name>/', views.recipient_page, name="recipient")
]
