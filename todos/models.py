
from django.db import models, transaction
from django.db.models import F
from django.utils.timezone import localtime, now

from hub.models import SharedSpace, User

######## Recurrent Todo helpers

class OrderedUser(models.Model):
    user = models.ForeignKey("hub.User", on_delete=models.CASCADE, null=True, blank=True)
    recurrent_todo = models.ForeignKey("todos.TodoRecurrency", on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    empty = models.BooleanField(default=False)

    def __str__(self):
        return f'OrderedUser: {self.user} - {self.recurrent_todo} | {self.order}'

class TodoRecurrency(models.Model):
    assigned_users = models.ManyToManyField("hub.User", through=OrderedUser)
    recurrency_turn = models.IntegerField(default=0, blank=False, null=False)
    started_at = models.DateField(auto_created=True, auto_now_add=True)
    day_rotation = models.IntegerField(default=7)

    def create_with_settings(users, rate):
        recurrency = TodoRecurrency.objects.create(recurrency_turn = 0, day_rotation = rate)

        for (i, user) in enumerate(users):
            if user:
                user = OrderedUser(user=user, recurrent_todo = recurrency, order = i)
                user.save()
            else:
                user = OrderedUser(empty = True, recurrent_todo = recurrency, order = i)
                user.save()


        return recurrency
    
    def add_user(self,user):
        OrderedUser(user=user, recurrent_todo = self, order = len(OrderedUser.objects.all(recurrent_todo = self)))
        OrderedUser.save()

    def add_empty(self):
        OrderedUser(empty = True, recurrent_todo = self, order = len(OrderedUser.objects.all(recurrent_todo = self)))
        OrderedUser.save()

    def get_user_at_day(self,n) -> User:
        users = OrderedUser.objects.filter(recurrent_todo = self).order_by("order")
        idx = (n // self.day_rotation) % len(users)
        return users[idx].user
    
    def get_full_order(self):
        """
        Returns the full list of users as a list of user objects. Empty users are shown as None
        """
        ordered_users = OrderedUser.objects.filter(recurrent_todo = self).order_by("order")
        return [ou.user for ou in ordered_users]
    
    def get_current_rotation(self):
        """
        Returns the current index of the user that is assigned to the todo
        """
        users = OrderedUser.objects.filter(recurrent_todo = self)

        current_time = localtime(now()).date()
        start_time = self.recurrent_state.started_at

        passed_days = (current_time - start_time).days
        return (passed_days // self.day_rotation) % len(users)



#######

class Todo(models.Model):
    name = models.CharField(max_length=500, blank=False, null=False)
    description = models.CharField(max_length=2000, blank=False, null=False)
    done = models.BooleanField(default=False)
    position = models.IntegerField()
    space = models.ForeignKey(SharedSpace, on_delete=models.CASCADE)
    recurrent_state = models.ForeignKey(TodoRecurrency, on_delete=models.CASCADE, blank=True, null=True)
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
        todo = Todo.objects.create(name="New Todo", description = "", position = max_pos+1, space=space)

        return todo

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

    def make_recurrent(self, users=[None], rate=7):
        """
        Turn the todo into a recurrent todo with the specified users and the specified rate.
        The users are ordered
        """
        recurrency = TodoRecurrency.create_with_settings(users, rate)

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

    def get_currently_assigned_user(self) -> User:
        if self.recurrent_state:
            current_time = localtime(now()).date()
            start_time = self.recurrent_state.started_at

            passed_time = current_time - start_time
            return self.recurrent_state.get_user_at_day(passed_time.days)
        
        return self.assigned_user
        
    def get_next_assigned_user(self) -> User:
        if self.recurrent_state:
            current_time = localtime(now()).date()
            start_time = self.recurrent_state.started_at

            passed_time = current_time - start_time
            return self.recurrent_state.get_user_at_day(passed_time.days + self.recurrent_state.day_rotation)
        
        return self.assigned_user

    


class SubTask(models.Model):
    title = models.CharField(max_length=500, blank=False, null=False)
    done = models.BooleanField(default=False)
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)

    def __str__(self):
        return f'SubTask: {self.title} on {self.todo.name}'
    
