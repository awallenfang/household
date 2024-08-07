from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.db.models import F
from django.contrib.auth.decorators import login_required

from hub.models import User

from .models import Todo

@login_required
def dashboard(request):
    """
    The initial dashboard to show the todos
    """
    todos = Todo.get_open()

    finished_todos = Todo.get_closed()

    return render(request, "todos/dashboard_full.html", {'todos': todos, 'finished_todos': finished_todos})

@login_required
@require_http_methods(['DELETE'])
def delete_todo(request, id):
    """
    Delete the todo with the given ID
    """
    Todo.objects.filter(id=id).delete()

    todos = Todo.get_open()

    finished_todos = Todo.get_closed()

    return render(request, "todos/components/todo_list.html", {'todos': todos, 'finished_todos': finished_todos})

@login_required
@require_http_methods(['POST'])
def add_todo(request):
    """
    Add a new todo with default values
    """
    space = User.objects.get(auth_user = request.user).selected_space
    Todo.create_in_space(space)

    todos = Todo.get_open()

    finished_todos = Todo.get_closed()

    return render(request, "todos/components/todo_list.html", {'todos': todos, 'finished_todos': finished_todos})

@login_required
@require_http_methods(['POST'])
def edit_todo(request, id):
    """
    Swap the todo with the editable version
    """
    todo = Todo.objects.get(id = id)
    return render(request, "todos/components/todo_edit.html", {"todo": todo})

@login_required
@require_http_methods(['POST'])
def finish_edit_todo(request, id):
    """
    Finish and submit the editing of a todo with the given ID
    """
    todo = Todo.objects.get(id = id)

    todo_name = request.POST.get("todo_name", todo.name)
    todo_description = request.POST.get("todo_description", todo.description)

    todo.name = todo_name
    todo.description = todo_description

    todo.save()

    return render(request, "todos/components/todo.html", {"todo": todo})

@login_required
@require_http_methods(['POST'])
def close_todo(request, id):
    """
    Set a todo as being done
    """
    todo = Todo.objects.get(id = id)

    todo.done = True
    todo.save()

    todos = Todo.get_open()

    finished_todos = Todo.get_closed()

    return render(request, "todos/components/todo_list.html", {"todos": todos, "finished_todos": finished_todos})

@login_required
@require_http_methods(['POST'])
def open_todo(request, id):
    """
    Reopen a done todo
    """
    todo = Todo.objects.get(id = id)

    todo.done = False
    todo.save()

    todos = Todo.get_open()

    finished_todos = Todo.get_closed()

    return render(request, "todos/components/todo_list.html", {"todos": todos, "finished_todos": finished_todos})

@login_required
@require_http_methods(['POST'])
def reorder(request, id, left, right, status):
    """
    Allows the reordering on the dashboard. This will be called once a todo is dropped on a droppable space.
    It will return the id of the dropped todo, as well as the position values on the left and the right of the space.
    If it is on the edges either left or right will be set to -1, since there is no space there.
    """
    # Move position
    changed_todo = Todo.objects.get(id=int(id))
    changed_todo.reorder(int(left), int(right))

    changed_todo.done = False if status == "open" else True

    changed_todo.save()

    todos = Todo.get_open()

    finished_todos = Todo.get_closed()

    return render(request, "todos/components/todo_list.html", {"todos": todos, "finished_todos": finished_todos})