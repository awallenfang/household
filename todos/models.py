from django.db import models, transaction
from django.db.models import F

from hub.models import SharedSpace, User

######## Recurrent Todo helpers

class _OrderedUser(models.Model):
    user = models.ForeignKey("hub.User")
    recurrent_todo = models.ForeignKey("todos.TodoRecurrency")
    order = models.IntegerField(default=0)

class _TodoRecurrency(models.Model):
    assigned_users = models.ManyToManyField("hub.User", through=_OrderedUser)
    recurrency_turn = models.IntegerField(default=0, blank=False, null=False)
    started_at = models.DateField(auto_created=True)
    day_rotation = models.IntegerField(default=7)

    def create_with_settings(users, rate):
        recurrency = _TodoRecurrency.objects.create(recurrency_turn = 0, day_rotation = rate)

        for (i, user) in enumerate(users):
            _OrderedUser(user=user, recurrent_todo = recurrency, order = i)
            _OrderedUser.save()

        return recurrency
    
    def add_user(self,user):
        _OrderedUser(user=user, recurrent_todo = self, order = len(_OrderedUser.objects.all(recurrent_todo = self)))
        _OrderedUser.save()

#######

class Todo(models.Model):
    name = models.CharField(max_length=500, blank=False, null=False)
    description = models.CharField(max_length=2000, blank=False, null=False)
    done = models.BooleanField(default=False)
    position = models.IntegerField()
    space = models.ForeignKey(SharedSpace, on_delete=models.CASCADE)
    recurrent_state = models.ForeignKey(_TodoRecurrency, on_delete=models.CASCADE, blank=True, null=True)
    assigned_user = models.ForeignKey("hub.User", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.name}: {self.description} | Position: {self.position} | Done: {self.done}'
    
    def create_in_space(space):
        """
        Create a todo with the name "New Todo" and an empty description
        """
        todos = Todo.objects.all()
        max_pos = 0
        if len(todos) > 0:
            Todo.minimize_positions()
            max_pos = Todo.objects.all().order_by('-position')[0].position
        Todo.objects.create(name="New Todo", description = "", position = max_pos+1, space=space)

    def get_open(request):
        user = User.objects.get(auth_user = request.user)
        space = user.selected_space
        return Todo.objects.filter(done=False, space=space).order_by("position")
    
    def get_closed(request):
        user = User.objects.get(auth_user = request.user)
        space = user.selected_space

        return Todo.objects.filter(done=True, space=space).order_by("position")
    
    def minimize_positions():
        """
        This minimizes all the values for the positions to not leave any holes
        """
        todos = Todo.objects.all().order_by('position')

        for (i,t) in enumerate(todos):
            t.position = i
            t.save()

    @transaction.atomic
    def reorder(self, left: int, right: int):
        """
        Reorder the todos in the overview. Left and right are the positions of the todos at those spaces. -1 is used if there is no todo there
        """
        # Left border
        if left == -1:
            self.position = int(right)

            todos_to_increment = Todo.objects.filter(position__gte=int(right))
            todos_to_increment.update(position=F('position') + 1)
        # Right border
        elif right == -1:
            self.position = int(left)+1
            
            todos_to_increment = Todo.objects.filter(position__gte=int(left)+1)
            todos_to_increment.update(position=F('position') + 1)
        else:
            todos_to_increment = Todo.objects.filter(position__gte=int(right))

            todos_to_increment.update(position=F('position') + 1)

            self.position = int(right)
        
        self.save()

        Todo.minimize_positions()
        
    def assign_user(self, user):
        """
        Assign a user to a todo that isn't recurrent
        """
        recurrency = self.recurrent_state
        if not recurrency:
            self.assigned_user = user
            self.save()

    def make_recurrent(self, users=[], rate=7):
        """
        Turn the todo into a recurrent todo with the specified users and the specified rate.
        The users are ordered
        """
        recurrency = _TodoRecurrency.create_with_settings(users, rate)

        self.recurrent_state = recurrency
        self.save()

    def add_recurrent_user(self, user):
        """
        Add a user to the recurrent todo
        """
        recurrency = self.recurrent_state
        if recurrency:
            recurrency.add_user(user)
            recurrency.save()

    


class SubTask(models.Model):
    title = models.CharField(max_length=500, blank=False, null=False)
    done = models.BooleanField(default=False)
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)

    def __str__(self):
        return f'SubTask: {self.title} on {self.todo.name}'
    
