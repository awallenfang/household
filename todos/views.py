from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


from .models import Todo

# Create your views here.
def dashboard(request):
    """
    The initial dashboard to show the todos
    """
    todos = Todo.objects.filter(done=False)

    finished_todos = Todo.objects.filter(done=True)

    return render(request, "todos/dashboard_full.html", {'todos': todos, 'finished_todos': finished_todos})

@require_http_methods(['DELETE'])
def delete_todo(request, id):
    """
    Delete the todo with the given ID
    """
    Todo.objects.filter(id=id).delete()

    todos = Todo.objects.filter(done=False)

    finished_todos = Todo.objects.filter(done=True)

    return render(request, "todos/components/todo_list.html", {'todos': todos, 'finished_todos': finished_todos})

@require_http_methods(['POST'])
def add_todo(request):
    """
    Add a new todo with default values
    """
    Todo.create_default()

    todos = Todo.objects.filter(done=False)

    finished_todos = Todo.objects.filter(done=True)

    return render(request, "todos/components/todo_list.html", {'todos': todos, 'finished_todos': finished_todos})

@require_http_methods(['POST'])
def edit_todo(request, id):
    """
    Swap the todo with the editable version
    """
    todo = Todo.objects.get(id = id)
    return render(request, "todos/components/todo_edit.html", {"todo": todo})

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

@require_http_methods(['POST'])
def close_todo(request, id):
    """
    Set a todo as being done
    """
    todo = Todo.objects.get(id = id)

    todo.done = True
    todo.save()

    todos = Todo.objects.filter(done=False)

    finished_todos = Todo.objects.filter(done=True)

    return render(request, "todos/components/todo_list.html", {"todos": todos, "finished_todos": finished_todos})

@require_http_methods(['POST'])
def open_todo(request, id):
    """
    Reopen a done todo
    """
    todo = Todo.objects.get(id = id)

    todo.done = False
    todo.save()

    todos = Todo.objects.filter(done=False)

    finished_todos = Todo.objects.filter(done=True)

    return render(request, "todos/components/todo_list.html", {"todos": todos, "finished_todos": finished_todos})