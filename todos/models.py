from django.db import models

# Create your models here.
class Todo(models.Model):
    name = models.CharField(max_length=500, blank=False, null=False)
    description = models.CharField(max_length=2000, blank=False, null=False)
    def __str__(self):
        return f'{self.name}: {self.description}'

class SubTask(models.Model):
    title = models.CharField(max_length=500, blank=False, null=False)
    done = models.BooleanField(default=False)

    def __str__(self):
        return f'SubTask: {self.title}'

class SubTaskToTodo(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    subtask = models.ForeignKey(SubTask, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.todo.name} - {self.subtask.title}'