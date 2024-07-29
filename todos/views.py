from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


from .models import Todo

# Create your views here.
def empty(request):
    return render(request, "todos/dashboard.html")

def dashboard(request):
    todos = Todo.objects.all()
    return render(request, "todos/dashboard_full.html", {'todos': todos})

@require_http_methods(['DELETE'])
def delete_todo(request, id):
    Todo.objects.filter(id=id).delete()
    todos = Todo.objects.all()
    return render(request, "todos/components/todo_list.html", {'todos': todos})

@require_http_methods(['POST'])
def add_todo(request):
    Todo.objects.create(name = "New todo", description = "A very interesting and useful description")
    todos = Todo.objects.all()
    return render(request, "todos/components/todo_list.html", {"todos": todos})

def edit_todo(request, id):
    todo = Todo.objects.get(id = id)
    return render(request, "todos/components/todo_edit.html", {"todo": todo})

def finish_edit_todo(request, id):
    # TODO: Add changes to db
    todo = Todo.objects.get(id = id)
    print(request.POST)
    todo_name = request.POST.get("todo_name", todo.name)
    todo_description = request.POST.get("todo_description", todo.description)

    todo.name = todo_name
    todo.description = todo_description

    todo.save()

    return render(request, "todos/components/todo.html", {"todo": todo})