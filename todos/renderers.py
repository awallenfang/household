from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from hub.decorators import space_required
from hub.models import Profile
from todos.models import Todo

@login_required
@space_required
def render_dashboard(request):
    todos = Todo.get_open(request)

    finished_todos = Todo.get_closed(request)

    user = Profile.objects.get(user = request.user)
    user_spaces = user.spaces.all()
    selected_space = user.selected_space

    return render(request, "todos/dashboard_full.html", {'todos': todos, 'finished_todos': finished_todos, 'user_spaces': user_spaces, 'selected_space': selected_space})

@login_required
@space_required
def render_todo_list(request, *args, **kwargs):
    todos = Todo.get_open(request)

    finished_todos = Todo.get_closed(request)

    return render(request, "todos/components/todo_list.html", {'todos': todos, 'finished_todos': finished_todos})

def empty(_request):
    return HttpResponse("")

@login_required
@space_required
def render_todo(request, todo_id, *args, **kwargs):
    todo = get_object_or_404(Todo, id=todo_id)
    profile = get_object_or_404(Profile, user = request.user)

    if todo.space in profile.spaces.all():
        return render(request, "todos/components/todo.html", {'todo': todo})
    else:
        return empty(request)

@login_required
@space_required
def render_schedule_editor(request, todo_id):
    todo = Todo.objects.get(id = todo_id)

    if todo.schedule_state is None:
        return empty(request)

    user = Profile.objects.get(user = request.user)

    if todo.space in user.spaces.all():
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