from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

# Create your views here.
def empty(request):
    return render(request, "hub/base.html")