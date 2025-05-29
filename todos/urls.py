from django.urls import path

from todos import renderers

from . import views

app_name = "todos"

urlpatterns = [
    path('', views.TodoDashboard.as_view(), name="todos"),
    path('add/', views.CreateTodoView.as_view(), name="add_todo"),
    path('<int:todo_id>/delete/', views.DeleteTodoView.as_view(), name="delete_todo"),
    path('<int:todo_id>/edit/', views.EditTodoView.as_view(), name="edit_todo"),
    path('<int:todo_id>', views.TodoDetailView.as_view(), name="todo"),
    path('<int:todo_id>/editor', views.ScheduleDetailView.as_view(), name="schedule_editor"),
    path('empty', renderers.empty, name="empty"),
]
