from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "space"

urlpatterns = [
    path('select_space/<int:space_id>', views.select_space, name="select_space"),
    path('create_space', views.create_space, name="create_space"),
    path('join_space', views.join_space, name="join_space"),
    path('<int:space_id>', views.space_view, name="space_view"),
]