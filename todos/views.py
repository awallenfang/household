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
def render_recurrency_editor(request, todo_id):
    todo = Todo.objects.get(id = todo_id)

    if todo.recurrent_state is None:
        return empty(request)

    user = Profile.objects.get(user = request.user)

    if todo.space in user.spaces:
        space_users = todo.space.joined_people()
        existing_order = todo.recurrent_state.get_full_order()
        current_assignment = todo.recurrent_state.recurrency_turn
        rate = todo.recurrent_state.day_rotation
        return render(request, 
                    "todos/components/recurrency_editor.html", 
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
def recurrency_editor(request, todo_id):
    """
    Show the recurrency editor for the given todo
    """
    user = Profile.objects.get(user = request.user)
    todo = Todo.objects.get(id = todo_id)
    if todo.space in user.spaces:
        return render_recurrency_editor(request, todo_id)
    else:
        return empty(request)

@login_required
@space_required
@require_http_methods(['POST'])
def recurrency_add_users(request, todo_id):
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
                    todo.recurrent_state.add_empty()
                else:
                    user = get_object_or_404(Profile, id = user_id)
                    todo.recurrent_state.add_user(user)

            return render_recurrency_editor(request, todo_id)
        else:
            return empty(request)

@login_required
@space_required
@require_http_methods(['POST'])
def recurrency_rate_change(request, todo_id, rate):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        if todo.recurrent_state is None:
            return render_recurrency_editor(request, todo_id)
        
        todo.recurrent_state.day_rotation = rate
        todo.recurrent_state.save()
        return render_recurrency_editor(request, todo_id)
    else:
        return empty(request)


@login_required
@space_required
@require_http_methods(['POST'])
def recurrency_delete_position(request, todo_id, position):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        # If it isn't recurrant do nothing
        if todo.recurrent_state is None or position < 0:
            return render_recurrency_editor(request, todo_id)
        
        todo.recurrent_state.remove_user_at_position(position)

        return render_recurrency_editor(request, todo_id)
    else:
        return empty(request)

@login_required
@space_required
def recurrency_reorder_user(request, todo_id, prev_pos, pos):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:

        if todo.recurrent_state is None:
            return render_recurrency_editor(request, todo_id)
        
        todo.recurrent_state.reorder_user(int(prev_pos), int(pos))

        return render_recurrency_editor(request, todo_id)
    else:
        return empty(request)

@login_required
@space_required
def make_recurrent(request, todo_id):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:

        user = Profile.objects.get(user = request.user)
        todo.make_recurrent([user])

        return render(request, "todos/components/todo.html", {"todo": todo})
    else:
        return empty(request)

@login_required
@space_required
def remove_recurrency(request, todo_id):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        user = Profile.objects.get(user = request.user)

        todo.recurrent_state = None
        todo.save()

        todo.assign_user(user)

        return render_todo_list(request)
    else:
        return empty(request)

@login_required
@space_required
def recurrency_set_position(request, todo_id, position):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        recurrent_state = todo.recurrent_state

        if recurrent_state is None:
            return render_todo_list(request)
        if position > len(recurrent_state.assigned_users.all()):
            recurrent_state.recurrency_turn = len(recurrent_state.assigned_users) - 1
        else:
            recurrent_state.recurrency_turn = position
        recurrent_state.save()
    
    
        return render_recurrency_editor(request, todo_id)
    else:
        return empty(request)



