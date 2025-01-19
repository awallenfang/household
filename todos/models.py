
from datetime import date
from django.db import models, transaction
from django.db.models import F
from django.utils.timezone import localtime, now

from hub.models import SharedSpace, User

######## Recurrent Todo helpers

class OrderedUser(models.Model):
    """
    Corresponds to the order of users in a recurrency
    """
    user = models.ForeignKey("hub.User", on_delete=models.CASCADE, null=True, blank=True)
    recurrent_todo = models.ForeignKey("todos.TodoRecurrency", on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    empty = models.BooleanField(default=False)

    def __str__(self):
        return f'OrderedUser: {self.user} - {self.recurrent_todo} | {self.order}'

class TodoRecurrency(models.Model):
    """
    Tracks the assignment of a todo along time with the todo opening up after some time and changing the assigned users
    """
    assigned_users = models.ManyToManyField("hub.User", through=OrderedUser)
    recurrency_turn = models.IntegerField(default=0, blank=False, null=False)
    started_at = models.DateField(auto_created=True, default=now)
    day_rotation = models.IntegerField(default=7)
    last_check = models.DateTimeField(auto_created=True, default=now)

    @staticmethod
    def create_with_settings(users, rate):
        """
        Create a TodoRecurrency with the specified users and recurrency_rate
        """
        recurrency = TodoRecurrency.objects.create(recurrency_turn = 0, day_rotation = rate)

        for (i, user) in enumerate(users):
            if user:
                user = OrderedUser(user=user, recurrent_todo = recurrency, order = i)
                user.save()
            else:
                user = OrderedUser(empty = True, recurrent_todo = recurrency, order = i)
                user.save()


        return recurrency
    
    def add_user(self, user):
        """
        Add a user to the TodoRecurrency
        """
        order = len(OrderedUser.objects.filter(recurrent_todo = self))
        ordered_user = OrderedUser.objects.create(user=user, recurrent_todo = self, order = order)
        ordered_user.save()

    def add_empty(self):
        """
        Add an empty field to the TodoRecurrency
        """
        order = len(OrderedUser.objects.filter(recurrent_todo = self))
        ordered_user = OrderedUser.objects.create(empty = True, recurrent_todo = self, order = order)
        ordered_user.save()

    def get_user_at_day(self, n) -> User:
        """
        Return the assigned user n days after the start. 
        This is used during testing mainly and does not properly track changes of the assigned position of the recurrency
        """
        users = OrderedUser.objects.filter(recurrent_todo = self).order_by("order")
        if len(users) == 0:
            return None
        idx = (n // self.day_rotation) % len(users)
        return users[idx].user
    
    def get_current_user(self) -> User:
        """
        Get the currently assigned user. 
        If there are no users or if there is no assigned user in the next turn return none
        """
        users = OrderedUser.objects.filter(recurrent_todo = self).order_by("order")
        if len(users) == 0:
            return None
        return users[self.recurrency_turn].user

    def get_next_user(self) -> User:
        """
        Get the user of the next turn. 
        If there are no users or if there is no assigned user in the next turn return none
        """
        users = OrderedUser.objects.filter(recurrent_todo = self).order_by("order")
        if len(users) == 0:
            return None
        return users[(self.recurrency_turn + 1) % len(users)].user
    
    def get_full_order(self):
        """
        Returns the full list of users as a list of user objects. Empty users are shown as None
        """
        ordered_users = OrderedUser.objects.filter(recurrent_todo = self).order_by("order")
        return [ou.user for ou in ordered_users]
    
    def remove_user_at_position(self, position):
        """
        Remove the user at the given position
        """
        ordered_users = OrderedUser.objects.filter(recurrent_todo = self).order_by("order")
        if position >= len(ordered_users):
            return
        
        ordered_users[position].delete()
        
        ordered_users = OrderedUser.objects.filter(recurrent_todo = self).order_by("order")
        for i, ord_usr in enumerate(ordered_users):
            ord_usr.order = i
            ord_usr.save()

        self.recurrency_turn = self.recurrency_turn % len(self.assigned_users.all())

    @transaction.atomic 
    def reorder_user(self, prev_pos, new_pos):
        """
        Reorder the users. 
        The user at prev_pos is moved to new_pos.
        All other users are moved accordingly to keep the ordering
        """
        user_amt = OrderedUser.objects.filter(recurrent_todo = self).count()
        if new_pos < 0 or prev_pos < 0 or new_pos > user_amt or prev_pos >= user_amt:
            return
        moved_users = OrderedUser.objects.filter(recurrent_todo = self, order__gte=new_pos).order_by("order")
        prev_user = OrderedUser.objects.get(recurrent_todo = self, order = prev_pos)
        for user in moved_users:
            user.order += 1
            user.save()
        prev_user.order = new_pos
        prev_user.save()

        ordered_users = OrderedUser.objects.filter(recurrent_todo = self).order_by("order")
        for i, ord_usr in enumerate(ordered_users):
            ord_usr.order = i
            ord_usr.save()


    def tick_rotation(self):
        """
        Ticks the recurrency rotation to continue it if there are day changes
        """
        date_now = now().date()
        last_date = self.last_check.date()
        if date_now > self.last_check.date():
            day_difference = (date_now - last_date).days
            if day_difference > 0:
                old_turn = self.recurrency_turn
                self.recurrency_turn += day_difference % len(self.assigned_users.all())
                new_turn = self.recurrency_turn

                if old_turn != new_turn:
                    user = self.get_current_user()
                    todo = Todo.objects.get(recurrent_state = self)

                    # If there are no users or this time no one is assigned set it to be closed
                    if user is None:
                        todo.set_closed()
                        todo.assigned_user = None
                        todo.save()
                    else:
                        todo.set_open()

                        todo.assigned_user = self.get_current_user()
                        todo.save()
                    
        self.last_check = now()
        self.save()

    

    def __str__(self):
        todo = Todo.objects.get(recurrent_state__id = self.id)
        return f'Recurrency for {todo.name} in {todo.space}'
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
    
    @staticmethod
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
    
    @staticmethod
    def get_open(request):
        user = User.objects.get(auth_user = request.user)
        space = user.selected_space
        return Todo.objects.filter(done=False, space=space).order_by("position")
    
    @staticmethod
    def get_closed(request):
        user = User.objects.get(auth_user = request.user)
        space = user.selected_space

        return Todo.objects.filter(done=True, space=space).order_by("position")
    
    @staticmethod
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
        if self.recurrent_state is not None:
            current_time = now().date()
            start_time = self.recurrent_state.started_at
            
            # This feels kinda disgusting, but ig it works. For some reason the DateField doesn't return the same date object as Djangos date method
            passed_time = current_time - date(start_time.year, start_time.month, start_time.day)
            return self.recurrent_state.get_user_at_day(passed_time.days)
        
        return self.assigned_user
        
    def get_next_assigned_user(self) -> User:
        if self.recurrent_state:
            current_time = now().date()
            start_time = self.recurrent_state.started_at

            passed_time = current_time - date(start_time.year, start_time.month, start_time.day)
            return self.recurrent_state.get_user_at_day(passed_time.days + self.recurrent_state.day_rotation)
        
        return self.assigned_user
    
    def set_open(self):
        self.done = False
        self.save()

    def set_closed(self):
        self.done = True
        self.save()
    
    @staticmethod
    def check_recurrency_update():

        recurrent_todos = Todo.objects.filter(recurrent_state__isnull = False)

        for todo in recurrent_todos:
            todo.recurrent_state.tick_rotation()

class SubTask(models.Model):
    title = models.CharField(max_length=500, blank=False, null=False)
    done = models.BooleanField(default=False)
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)

    def __str__(self):
        return f'SubTask: {self.title} on {self.todo.name}'
    
