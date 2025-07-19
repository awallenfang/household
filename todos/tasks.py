from celery import shared_task

from todos.models import Todo
import logging
@shared_task
def update_todo_schedules():
    logging.info("RUNNING")
    Todo.check_schedule_update()