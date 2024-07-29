"""
URL configuration for p project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.dashboard, name="todos"),
    path('<int:id>/delete/', views.delete_todo, name="delete_todo"),
    path('add/', views.add_todo, name="add_todo"),
    path('<int:id>/edit/', views.edit_todo, name="edit_todo"),
    path('<int:id>/finish_edit/', views.finish_edit_todo, name="finish_todo_edit"),

]
