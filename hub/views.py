from django.db import IntegrityError
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .forms import LoginForm, SignupForm
from .models import Profile
from todos.models import Todo

@login_required
def hub(request):
    user = Profile.objects.get(user = request.user)
        
    user_spaces = user.spaces.all()
    selected_space = user.selected_space

    open_todo_amt = Todo.objects.filter(space = selected_space, done = False).count()
    closed_todo_amt = Todo.objects.filter(space = selected_space, done = True).count()
    assigned_todo_amt = Todo.objects.filter(space = selected_space, done = False, assigned_user = user).count()

    context = {"user_spaces": user_spaces, 
    "selected_space": selected_space,
    "open_todo_amt": open_todo_amt,
    "closed_todo_amt": closed_todo_amt,
    "open_assigned_todo_amt": assigned_todo_amt,
    "open_todos_due": 42}
    return render(request, 
                    "hub/hub.html", 
                    context)
    
def login(request):
    # If the user is alread logged in, redirect
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if request.method == "GET":
        form = LoginForm()
        return render(request, "hub/login.html", {'form': form})
    
    
    form = LoginForm(request.POST)
    if form.is_valid():
        auth_user = auth.authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])

        if auth_user:
            auth.login(request, auth_user)

            return HttpResponseRedirect("/")
        
        return render(request, "hub/login.html", {"form": form, "error_message": "The input data is incorrect!"})
    
    return render(request, "hub/login.html", {"form": form, "error_message": "The input data is incorrect!"})
        
def signup(request):
    # If the user is alread logged in, redirect
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    
    if request.method == "GET":
        form = SignupForm()
        return render(request, "hub/signup.html", {'form': form})
    
    
    form = SignupForm(request.POST)

    if form.is_valid():

        # Catch invalid repeat password
        if form.cleaned_data["password"]  != form.cleaned_data["repeat_password"]:
            return render(request, "hub/signup.html", {"form": form, "error_message": "The passwords don't match."})
        
        # Create the user. If the username is already taken, return an error stating it
        try:
            auth_user = User.objects.create_user(form.cleaned_data["username"], form.cleaned_data["email"], form.cleaned_data["password"])
        except IntegrityError:
            return render(request, "hub/signup.html", {"form": form, "error_message": "The username is already taken."})
        
        # If the auth_user was created, also create out user model
        Profile.objects.create(user=auth_user)

        # If everything was successful return to the hub
        return HttpResponseRedirect("/login")
   
    # If something is wrong in the valid, check what it is and return a corresponding error
    return render(request, "hub/signup.html", {"form": form, "error_message": "There is a problem in the form!"})

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")

