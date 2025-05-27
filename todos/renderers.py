from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
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
