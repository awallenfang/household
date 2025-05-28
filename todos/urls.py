from django.urls import path

from todos import renderers

from . import views

app_name = "todos"

urlpatterns = [
    path('', views.TodoDashboard.as_view(), name="todos"),
    path('add/', views.CreateTodoView.as_view(), name="add_todo"),
    path('<int:todo_id>/delete/', views.DeleteTodoView.as_view(), name="delete_todo"),

    path('<int:todo_id>/<str:left>/<str:right>/<str:status>/reorder', views.reorder, name="todo_reorder"),

    path('<int:pk>/edit/', views.EditTodoView.as_view(), name="edit_todo"),
    path('<int:todo_id>/finish_edit/', views.finish_edit_todo, name="finish_todo_edit"),

    path('<int:todo_id>/close_todo/', views.close_todo, name="close_todo"),
    path('<int:todo_id>/open_todo/', views.open_todo, name="open_todo"),
    path('<int:todo_id>/make_recurrent', views.make_recurrent, name="make_recurrent"),
    path('<int:todo_id>/editor', views.recurrency_editor, name="recurrency_editor"),
    path('<int:todo_id>/add_users', views.recurrency_add_users, name="recurrency_add_users"),
    path('<int:todo_id>/rate_change/<int:rate>', views.recurrency_rate_change, name="recurrency_rate_change"),
    # Maybe move this path to the hub
    path('empty', renderers.empty, name="empty"),
    path('<int:todo_id>/remove_position/<int:position>', views.recurrency_delete_position, name="recurrency_remove_position"),
    path('<int:todo_id>/<int:prev_pos>/<int:pos>/recurrency_reorder_user', views.recurrency_reorder_user, name="todo_recurrency_reorder_user"),
    path('<int:todo_id>/remove_recurrency', views.remove_recurrency, name="remove_recurrency"),
    path('<int:todo_id>/<int:position>/recurrency_set_position', views.recurrency_set_position, name="todo_recurrency_set_position"),

]
