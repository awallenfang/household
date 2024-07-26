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
    return render(request, "todos/dashboard.html", {'todos': todos})