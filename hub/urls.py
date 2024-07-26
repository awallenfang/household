from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    # path('', include("transactions.urls")),
    # path('todos/', include("todos.urls")),
    path('', views.empty, name="hub"),

]