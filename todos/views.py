from functools import wraps
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, View, CreateView, FormView, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator


from hub.decorators import space_required
from hub.mixins import HTMXMixin
from hub.models import Profile
from todos.forms import TodoForm
from todos.renderers import *
from todos.actions import *

from .models import Todo

@method_decorator(login_required, name='dispatch')
@method_decorator(space_required, name='dispatch')
class TodoDashboard(HTMXMixin, ListView):
    model = Todo
    template_name = "todos/dashboard_full.html"
    context_object_name = "todos"
    partials = {
        "todo_list": render_todo_list
    }
    
    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        return Todo.objects.filter(space=profile.selected_space).order_by('position', 'done')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todos = Todo.get_open(self.request)

        finished_todos = Todo.get_closed(self.request)

        user = Profile.objects.get(user = self.request.user)
        user_spaces = user.spaces.all()
        selected_space = user.selected_space
        context.update({
            'todos': todos,
            'finished_todos': finished_todos,
            'user_spaces': user_spaces,
            'selected_space': selected_space
        })
        return context
    
    def delete(self, request, *args, **kwargs):
        """
        Handle the deletion of a todo item.
        """
        todo_id = kwargs.get('pk')
        todo = get_object_or_404(Todo, id=todo_id)
        
        if todo.space == Profile.objects.get(user=request.user).selected_space:
            todo.delete()
        
        return render_todo_list(request)


class DeleteTodoView(HTMXMixin, View):
    partials = {
        "todo_list": (render_todo_list, delete_todo)
    }

    def delete(self, request, todo_id):
        delete_todo(todo_id)

class CreateTodoView(HTMXMixin, View):
    model = Todo
    partials = {
        "create_todo": (render_todo_list, create_todo)
    }

    def get(self, request, *args, **kwargs):
        create_todo(request, *args, **kwargs)
        return redirect("todos:todos")
    
    def post(self, request, *args, **kwargs):
        create_todo(request, *args, **kwargs)
        return redirect("todos:todos")

class EditTodoView(UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = "todos/components/todo_edit.html"
    pk_url_kwarg = "todo_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For some reason this doesn't populate the form properly
        context["form"] = self.form_class(instance=self.get_object())
        return context
    
    def form_valid(self, form):
        if form.is_valid():
            todo = form.save()
        return render_todo(self.request, self.get_object().id)

@login_required
@space_required
@require_http_methods(['POST'])
def close_todo(request, todo_id):
    """
    Set a todo as being done
    """
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        todo.done = True
        todo.save()

        todos = Todo.get_open(request)

        finished_todos = Todo.get_closed(request)

        return render(request, "todos/components/todo_list.html", {"todos": todos, "finished_todos": finished_todos})
    else:
        return empty(request)

@login_required
@space_required
@require_http_methods(['POST'])
def open_todo(request, todo_id):
    """
    Reopen a done todo
    """
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        todo.done = False
        todo.save()

        return render_todo_list(request)
    else:
        return empty()


@login_required
@space_required
def reorder(request, todo_id, left, right, status):
    """
    Allows the reordering on the dashboard. This will be called once a todo is dropped on a droppable space.
    It will return the id of the dropped todo, as well as the position values on the left and the right of the space.
    If it is on the edges either left or right will be set to -1, since there is no space there.
    """
    # Move position
    changed_todo = Todo.objects.get(id=int(todo_id))

    if changed_todo.space == Profile.objects.get(user = request.user).selected_space:
        changed_todo.reorder(int(left), int(right))

        changed_todo.done =  not (status == "open") 

        changed_todo.save()

    return HttpResponse()

@login_required
@space_required
def render_schedule_editor(request, todo_id):
    todo = Todo.objects.get(id = todo_id)

    if todo.schedule_state is None:
        return empty(request)

    user = Profile.objects.get(user = request.user)

    if todo.space in user.spaces:
        space_users = todo.space.joined_people()
        existing_order = todo.schedule_state.get_full_order()
        current_assignment = todo.schedule_state.schedule_turn
        rate = todo.schedule_state.day_rotation
        return render(request, 
                    "todos/components/schedule_editor.html", 
                    {"todo": todo, 
                    "available_users": space_users, 
                    "existing_order": existing_order, 
                    "current_assignment_idx": current_assignment, 
                    "rate": rate})
    else:
        return empty(request)

@login_required
@space_required
@require_http_methods(['GET'])
def schedule_editor(request, todo_id):
    """
    Show the schedule editor for the given todo
    """
    user = Profile.objects.get(user = request.user)
    todo = Todo.objects.get(id = todo_id)
    if todo.space in user.spaces:
        return render_schedule_editor(request, todo_id)
    else:
        return empty(request)

@login_required
@space_required
@require_http_methods(['POST'])
def schedule_add_users(request, todo_id):
    # TODO: Figure out why the parameter isn't caught
    path = request.get_full_path()
    users = path.split("?users=")
    if len(users) > 1:
        added_list = users[1].split(",")
        ids = [int(id) for id in added_list]

        todo = Todo.objects.get(id = todo_id)
        if todo.space == Profile.objects.get(user = request.user).selected_space:
            for user_id in ids:
                if user_id == -1:
                    todo.schedule_state.add_empty()
                else:
                    user = get_object_or_404(Profile, id = user_id)
                    todo.schedule_state.add_user(user)

            return render_schedule_editor(request, todo_id)
        else:
            return empty(request)

@login_required
@space_required
@require_http_methods(['POST'])
def schedule_add_users(request, todo_id, rate):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        if todo.schedule_state is None:
            return render_schedule_editor(request, todo_id)
        
        todo.schedule_state.day_rotation = rate
        todo.schedule_state.save()
        return render_schedule_editor(request, todo_id)
    else:
        return empty(request)


@login_required
@space_required
@require_http_methods(['POST'])
def schedule_delete_position(request, todo_id, position):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        # If it isn't scheduled do nothing
        if todo.schedule_state is None or position < 0:
            return render_schedule_editor(request, todo_id)
        
        todo.schedule_state.remove_user_at_position(position)

        return render_schedule_editor(request, todo_id)
    else:
        return empty(request)

@login_required
@space_required
def schedule_reorder_user(request, todo_id, prev_pos, pos):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:

        if todo.schedule_state is None:
            return render_schedule_editor(request, todo_id)
        
        todo.schedule_state.reorder_user(int(prev_pos), int(pos))

        return render_schedule_editor(request, todo_id)
    else:
        return empty(request)

@login_required
@space_required
def make_scheduled(request, todo_id):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:

        user = Profile.objects.get(user = request.user)
        todo.make_scheduled([user])

        return render(request, "todos/components/todo.html", {"todo": todo})
    else:
        return empty(request)

@login_required
@space_required
def remove_schedule(request, todo_id):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        user = Profile.objects.get(user = request.user)

        todo.schedule_state = None
        todo.save()

        todo.assign_user(user)

        return render_todo_list(request)
    else:
        return empty(request)

@login_required
@space_required
def schedule_set_position(request, todo_id, position):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        schedule = todo.schedule_state

        if schedule is None:
            return render_todo_list(request)
        if position > len(schedule.assigned_users.all()):
            schedule.schedule_turn = len(schedule.assigned_users) - 1
        else:
            schedule.schedule_turn = position
        schedule.save()
    
    
        return render_schedule_editor(request, todo_id)
    else:
        return empty(request)




