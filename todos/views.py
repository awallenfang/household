from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def empty(request):
    return render(request, "todos/dashboard.html")