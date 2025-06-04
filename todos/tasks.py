from celery import shared_task

from todos.models import Todo

@shared_task
def update_todo_schedules():
    Todo.check_schedule_update()