from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from hub.models import User

from .models import Todo

@login_required
def dashboard(request):
    """
    The initial dashboard to show the todos
    """
    todos = Todo.get_open(request)

    finished_todos = Todo.get_closed(request)

    user = User.objects.get(auth_user = request.user)
    user_spaces = user.spaces.all()
    selected_space = user.selected_space

    return render(request, "todos/dashboard_full.html", {'todos': todos, 'finished_todos': finished_todos, 'user_spaces': user_spaces, 'selected_space': selected_space})

@login_required
@require_http_methods(['DELETE'])
def delete_todo(request, todo_id):
    """
    Delete the todo with the given ID
    """
    Todo.objects.filter(id=todo_id).delete()

    todos = Todo.get_open(request)

    finished_todos = Todo.get_closed(request)

    return render(request, "todos/components/todo_list.html", {'todos': todos, 'finished_todos': finished_todos})

@login_required
@require_http_methods(['POST'])
def add_todo(request):
    """
    Add a new todo with default values
    """
    user  = User.objects.get(auth_user = request.user)

    todo = Todo.create_in_space(user.selected_space)
    todo.assign_user(user)
    todos = Todo.get_open(request)

    finished_todos = Todo.get_closed(request)

    return render(request, "todos/components/todo_list.html", {'todos': todos, 'finished_todos': finished_todos})

@login_required
@require_http_methods(['POST'])
def edit_todo(request, todo_id):
    """
    Swap the todo with the editable version
    """
    todo = Todo.objects.get(id = todo_id)
    return render(request, "todos/components/todo_edit.html", {"todo": todo})

@login_required
@require_http_methods(['POST'])
def finish_edit_todo(request, todo_id):
    """
    Finish and submit the editing of a todo with the given ID
    """
    todo = Todo.objects.get(id = todo_id)

    todo_name = request.POST.get("todo_name", todo.name)
    todo_description = request.POST.get("todo_description", todo.description)

    todo.name = todo_name
    todo.description = todo_description

    todo.save()

    return render(request, "todos/components/todo.html", {"todo": todo})

@login_required
@require_http_methods(['POST'])
def close_todo(request, todo_id):
    """
    Set a todo as being done
    """
    todo = Todo.objects.get(id = todo_id)

    todo.done = True
    todo.save()

    todos = Todo.get_open(request)

    finished_todos = Todo.get_closed(request)

    return render(request, "todos/components/todo_list.html", {"todos": todos, "finished_todos": finished_todos})

@login_required
@require_http_methods(['POST'])
def open_todo(request, todo_id):
    """
    Reopen a done todo
    """
    todo = Todo.objects.get(id = todo_id)

    todo.done = False
    todo.save()

    todos = Todo.get_open(request)

    finished_todos = Todo.get_closed(request)

    return render(request, "todos/components/todo_list.html", {"todos": todos, "finished_todos": finished_todos})

@login_required
@require_http_methods(['POST'])
def reorder(request, todo_id, left, right, status):
    """
    Allows the reordering on the dashboard. This will be called once a todo is dropped on a droppable space.
    It will return the id of the dropped todo, as well as the position values on the left and the right of the space.
    If it is on the edges either left or right will be set to -1, since there is no space there.
    """
    # Move position
    changed_todo = Todo.objects.get(id=int(todo_id))
    changed_todo.reorder(int(left), int(right))

    changed_todo.done =  not (status == "open") 

    changed_todo.save()

    todos = Todo.get_open(request)

    finished_todos = Todo.get_closed(request)

    return render(request, "todos/components/todo_list.html", {"todos": todos, "finished_todos": finished_todos})

@login_required
@require_http_methods(['GET'])
def recurrency_editor(request, todo_id):
    """
    Show the recurrency editor for the given todo
    """
    todo = Todo.objects.get(id = todo_id)
    space_users = todo.space.users.all()
    existing_order = todo.recurrent_state.get_full_order()
    current_assignment = todo.recurrent_state.get_current_rotation()
    return render(request, "todos/components/recurrency_editor.html", {"todo": todo, "available_users": space_users, "existing_order": existing_order, "current_assignment_idx": current_assignment})