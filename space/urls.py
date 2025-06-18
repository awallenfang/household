from django.urls import path

from . import views

app_name = "space"

urlpatterns = [
    path('<int:space_id>', views.SpaceSettingsView.as_view(), name="space_view"),

    path('<int:space_id>/delete', views.delete_space, name="delete_space"),
    path('select_space/<int:space_id>', views.select_space, name="select_space"),
    path('create_space', views.create_space, name="create_space"),
    path('join_space', views.join_space, name="join_space"),
    path('leave_space/<int:space_id>', views.leave_space, name="leave_space"),
]