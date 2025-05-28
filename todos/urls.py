from django.urls import path

from todos import renderers

from . import views

app_name = "todos"

urlpatterns = [
    path('', views.TodoDashboard.as_view(), name="todos"),
    path('add/', views.CreateTodoView.as_view(), name="add_todo"),
    path('<int:todo_id>/delete/', views.DeleteTodoView.as_view(), name="delete_todo"),

    path('<int:todo_id>/<str:left>/<str:right>/<str:status>/reorder', views.reorder, name="todo_reorder"),

    path('<int:todo_id>/edit/', views.edit_todo, name="edit_todo"),
    path('<int:todo_id>/finish_edit/', views.finish_edit_todo, name="finish_todo_edit"),
    
    path('<int:todo_id>/close_todo/', views.close_todo, name="close_todo"),
    path('<int:todo_id>/open_todo/', views.open_todo, name="open_todo"),
    path('<int:todo_id>/make_scheduled', views.make_scheduled, name="make_scheduled"),
    path('<int:todo_id>/editor', views.schedule_editor, name="schedule_editor"),
    path('<int:todo_id>/add_users', views.schedule_add_users, name="schedule_add_users"),
    path('<int:todo_id>/rate_change/<int:rate>', views.schedule_add_users, name="schedule_add_users"),
    # Maybe move this path to the hub
    path('empty', renderers.empty, name="empty"),
    path('<int:todo_id>/remove_position/<int:position>', views.schedule_delete_position, name="schedule_delete_position"),
    path('<int:todo_id>/<int:prev_pos>/<int:pos>/schedule_reorder_user', views.schedule_reorder_user, name="schedule_reorder_user"),
    path('<int:todo_id>/remove_schedule', views.remove_schedule, name="remove_schedule"),
    path('<int:todo_id>/<int:position>/schedule_set_position', views.schedule_set_position, name="todo_schedule_set_position"),

]
