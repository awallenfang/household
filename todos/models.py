
from datetime import date
from django.db import models, transaction
from django.db.models import F
from django.utils.functional import cached_property
from django.utils.timezone import localtime, now
from django.utils.translation import gettext_lazy as _
from hub.models import SharedSpace, Profile

######## Scheduled Todo helpers

class OrderedUser(models.Model):
    """
    Corresponds to the order of users in a schedule
    """
    user = models.ForeignKey("hub.Profile", verbose_name=_("User"), on_delete=models.CASCADE, null=True, blank=True)
    scheduled_todo = models.ForeignKey("todos.TodoSchedule", verbose_name=_("Todo Schedule"), on_delete=models.CASCADE)
    order = models.IntegerField(default=0, verbose_name=_("Order"))
    empty = models.BooleanField(default=False, verbose_name=_("Empty"))

    def __str__(self):
        return f'OrderedUser: {self.user} - {self.scheduled_todo} | {self.order}'

class TodoSchedule(models.Model):
    """
    Tracks the assignment of a todo along time with the todo opening up after some time and changing the assigned users
    """
    assigned_users = models.ManyToManyField("hub.Profile", verbose_name=_("User"), through=OrderedUser)
    schedule_turn = models.IntegerField(default=0, verbose_name=_("Schedule Turn"), blank=False, null=False)
    started_at = models.DateField(auto_created=True, verbose_name=_("Started at"), default=now)
    day_rotation = models.IntegerField(default=7, verbose_name=_("Day rotation"))
    last_check = models.DateTimeField(auto_created=True, verbose_name=_("Last check"), default=now)

    @staticmethod
    def create_with_settings(users, rate):
        """
        Create a TodoSchedule with the specified users and schedule_rate
        """
        schedule = TodoSchedule.objects.create(schedule_turn = 0, day_rotation = rate)

        for (i, user) in enumerate(users):
            if user:
                user = OrderedUser(user=user, scheduled_todo = schedule, order = i)
                user.save()
            else:
                user = OrderedUser(empty = True, scheduled_todo = schedule, order = i)
                user.save()


        return schedule
    
    def add_user(self, user):
        """
        Add a user to the TodoSchedule
        """
        order = len(OrderedUser.objects.filter(scheduled_todo = self))
        ordered_user = OrderedUser.objects.create(user=user, scheduled_todo = self, order = order)
        ordered_user.save()

    def add_empty(self):
        """
        Add an empty field to the TodoSchedule
        """
        order = len(OrderedUser.objects.filter(scheduled_todo = self))
        ordered_user = OrderedUser.objects.create(empty = True, scheduled_todo = self, order = order)
        ordered_user.save()

    def get_user_at_day(self, n) -> Profile:
        """
        Return the assigned user n days after the start. 
        This is used during testing mainly and does not properly track changes of the assigned position of the schedule
        """
        users = OrderedUser.objects.filter(scheduled_todo = self).order_by("order")
        if len(users) == 0:
            return None
        idx = (n // self.day_rotation) % len(users)
        return users[idx].user
    
    @cached_property
    def get_current_user(self) -> Profile:
        """
        Get the currently assigned user. 
        If there are no users or if there is no assigned user in the next turn return none
        """
        users = OrderedUser.objects.filter(scheduled_todo = self).order_by("order")
        if len(users) == 0:
            return None
        if self.schedule_turn >= len(users):
            self.schedule_turn = self.schedule_turn % len(users)
        return users[self.schedule_turn].user

    @cached_property
    def get_next_user(self) -> Profile:
        """
        Get the user of the next turn. 
        If there are no users or if there is no assigned user in the next turn return none
        """
        users = OrderedUser.objects.filter(scheduled_todo = self).order_by("order")
        if len(users) == 0:
            return None
        return users[(self.schedule_turn + 1) % len(users)].user
    
    @cached_property
    def get_full_order(self):
        """
        Returns the full list of users as a list of user objects. Empty users are shown as None
        """
        ordered_users = OrderedUser.objects.filter(scheduled_todo = self).order_by("order")
        return [ou.user for ou in ordered_users]
    
    def remove_user_at_position(self, position):
        """
        Remove the user at the given position
        """
        ordered_users = OrderedUser.objects.filter(scheduled_todo = self).order_by("order")
        if position >= len(ordered_users):
            return
        
        ordered_users[position].delete()
        
        ordered_users = OrderedUser.objects.filter(scheduled_todo = self).order_by("order")
        for i, ord_usr in enumerate(ordered_users):
            ord_usr.order = i
            ord_usr.save()
        if self.ordereduser_set.count() > 0:
            self.schedule_turn = self.schedule_turn % self.ordereduser_set.count()
        else:
            self.schedule_turn = 0
            
    @transaction.atomic 
    def reorder_user(self, prev_pos, new_pos):
        """
        Reorder the users. 
        The user at prev_pos is moved to new_pos.
        All other users are moved accordingly to keep the ordering
        """
        user_amt = OrderedUser.objects.filter(scheduled_todo = self).count()
        if new_pos < 0 or prev_pos < 0 or new_pos > user_amt or prev_pos >= user_amt:
            return
        moved_users = OrderedUser.objects.filter(scheduled_todo = self, order__gte=new_pos).order_by("order")
        prev_user = OrderedUser.objects.get(scheduled_todo = self, order = prev_pos)
        for user in moved_users:
            user.order += 1
            user.save()
        prev_user.order = new_pos
        prev_user.save()

        ordered_users = OrderedUser.objects.filter(scheduled_todo = self).order_by("order")
        for i, ord_usr in enumerate(ordered_users):
            ord_usr.order = i
            ord_usr.save()


    def tick_rotation(self):
        """
        Ticks the schedule rotation to continue it if there are day changes
        """
        date_now = now().date()
        last_date = self.last_check.date()
        if date_now > self.last_check.date():
            day_difference = (date_now - last_date).days
            if day_difference > 0:
                old_turn = self.schedule_turn
                self.schedule_turn = (self.schedule_turn + day_difference) % self.ordereduser_set.count()
                new_turn = self.schedule_turn

                if old_turn != new_turn:
                    user = self.get_current_user()
                    todo = Todo.objects.get(schedule_state = self)

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
        todo = self.todo
        return f'Schedule for {todo.name} in {todo.space}'
#######

class Todo(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=500, blank=False, null=False)
    description = models.CharField(verbose_name=_("Description"), max_length=2000, blank=False, null=False)
    done = models.BooleanField(verbose_name=_("Done"), default=False)
    position = models.IntegerField(verbose_name=_("Position"))
    space = models.ForeignKey(SharedSpace, verbose_name=("Space"), on_delete=models.CASCADE)
    schedule_state = models.ForeignKey(TodoSchedule, verbose_name=_("Schedule"), on_delete=models.CASCADE, blank=True, null=True)
    assigned_user = models.ForeignKey("hub.Profile", verbose_name=_("Assigned user"), on_delete=models.CASCADE, blank=True, null=True)

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
        user = Profile.objects.get(user = request.user)
        space = user.selected_space
        return Todo.objects.filter(done=False, space=space).order_by("position")
    
    @staticmethod
    def get_closed(request):
        user = Profile.objects.get(user = request.user)
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
        Assign a user to a todo that isn't scheduled
        """
        schedule = self.schedule_state
        if not schedule:
            self.assigned_user = user
            self.save()

    def make_scheduled(self, users=[None], rate=7):
        """
        Turn the todo into a scheduled todo with the specified users and the specified rate.
        The users are ordered
        """
        schedule = TodoSchedule.create_with_settings(users, rate)

        self.schedule_state = schedule
        self.save()

    def add_scheduled_user(self, user):
        """
        Add a user to the scheduled todo
        """
        schedule = self.schedule_state
        if schedule:
            schedule.add_user(user)
            schedule.save()

    @cached_property
    def get_currently_assigned_user(self) -> Profile:
        if self.schedule_state is not None:
            current_time = now().date()
            start_time = self.schedule_state.started_at
            
            # This feels kinda disgusting, but ig it works. For some reason the DateField doesn't return the same date object as Djangos date method
            passed_time = current_time - date(start_time.year, start_time.month, start_time.day)
            return self.schedule_state.get_user_at_day(passed_time.days)
        
        return self.assigned_user
    
    @cached_property
    def get_next_assigned_user(self) -> Profile:
        if self.schedule_state:
            current_time = now().date()
            start_time = self.schedule_state.started_at

            passed_time = current_time - date(start_time.year, start_time.month, start_time.day)
            return self.schedule_state.get_user_at_day(passed_time.days + self.schedule_state.day_rotation)
        
        return self.assigned_user
    
    def set_open(self):
        self.done = False
        self.save()

    def set_closed(self):
        self.done = True
        self.save()
    
    @staticmethod
    def check_schedule_update():

        scheduled_todos = Todo.objects.filter(schedule_state__isnull = False)

        for todo in scheduled_todos:
            todo.schedule_state.tick_rotation()

class SubTask(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=500, blank=False, null=False)
    done = models.BooleanField(verbose_name=_("Done"), default=False)
    todo = models.ForeignKey(Todo, verbose_name=_("Todo"), on_delete=models.CASCADE)

    def __str__(self):
        return f'SubTask: {self.title} on {self.todo.name}'
    
