from django.urls import path

from . import views

app_name = "todos"

urlpatterns = [
    path('', views.dashboard, name="todos"),
    path('<int:todo_id>/delete/', views.delete_todo, name="delete_todo"),
    path('add/', views.add_todo, name="add_todo"),
    path('<int:todo_id>/edit/', views.edit_todo, name="edit_todo"),
    path('<int:todo_id>/finish_edit/', views.finish_edit_todo, name="finish_todo_edit"),
    path('<int:todo_id>/close_todo/', views.close_todo, name="close_todo"),
    path('<int:todo_id>/open_todo/', views.open_todo, name="open_todo"),
    path('<int:todo_id>/<str:left>/<str:right>/<str:status>/reorder', views.reorder, name="todo_reorder"),
    path('<int:todo_id>/editor', views.recurrency_editor, name="recurrency_editor"),
    path('<int:todo_id>/add_users', views.recurrency_add_users, name="recurrency_add_users"),
    path('<int:todo_id>/rate_change/<int:rate>', views.recurrency_rate_change, name="recurrency_rate_change"),
    # Maybe move this path to the hub
    path('empty', views.empty, name="empty"),
    path('<int:todo_id>/remove_position/<int:position>', views.recurrency_delete_position, name="recurrency_remove_position"),
    path('<int:todo_id>/<str:prev_pos>/<str:pos>/recurrency_reorder_user', views.recurrency_reorder_user, name="todo_recurrency_reorder_user"),

]
