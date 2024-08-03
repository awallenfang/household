from django.db import models

# Create your models here.
class Todo(models.Model):
    name = models.CharField(max_length=500, blank=False, null=False)
    description = models.CharField(max_length=2000, blank=False, null=False)
    done = models.BooleanField(default=False)
    position = models.IntegerField()

    def __str__(self):
        return f'{self.name}: {self.description} | Position: {self.position} | Done: {self.done}'
    
    def create_default():
        """
        Create a todo with the name "New Todo" and an empty description
        """
        max_pos = Todo.objects.all().order_by('-position')[0].position
        Todo.objects.create(name="New Todo", description = "", position = max_pos+1)

        Todo.minimize_positions()

    def get_open():
        return Todo.objects.filter(done=False).order_by("position")
    
    def get_closed():
        return Todo.objects.filter(done=True).order_by("position")
    
    def minimize_positions():
        """
        This minimizes all the values for the positions to not leave any holes
        """
        todos = Todo.objects.all().order_by('position')

        for (i,t) in enumerate(todos):
            t.position = i
            t.save()

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