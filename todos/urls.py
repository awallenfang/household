from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.dashboard, name="todos"),
    path('<int:id>/delete/', views.delete_todo, name="delete_todo"),
    path('add/', views.add_todo, name="add_todo"),
    path('<int:id>/edit/', views.edit_todo, name="edit_todo"),
    path('<int:id>/finish_edit/', views.finish_edit_todo, name="finish_todo_edit"),
    path('<int:id>/close_todo/', views.close_todo, name="close_todo"),
    path('<int:id>/open_todo/', views.open_todo, name="open_todo"),


]
