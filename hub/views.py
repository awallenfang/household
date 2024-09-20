from django.db import IntegrityError
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods



from .forms import LoginForm, SignupForm
from .models import SharedSpace, User



def hub(request):
    if request.user.is_authenticated:
        user = User.objects.get(auth_user = request.user)
        user_spaces = user.spaces.all()
        selected_space = user.selected_space
        return render(request, 
                      "hub/base.html", 
                      {"user_spaces": user_spaces, "selected_space": selected_space})
    else:
        return HttpResponseRedirect("/login")

def login(request):
    # If the user is alread logged in, redirect
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if request.method == "GET":
        form = LoginForm()
        return render(request, "hub/login.html", {'form': form})
    
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            auth_user = auth.authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])

            if auth_user:
                auth.login(request, auth_user)

                return HttpResponseRedirect("/")
            else:
                return render(request, "hub/login.html", {"form": form, "error_message": "The input data is incorrect!"})
        else: 
            return render(request, "hub/login.html", {"form": form, "error_message": "The input data is incorrect!"})
        
def signup(request):
    # If the user is alread logged in, redirect
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    
    if request.method == "GET":
        form = SignupForm()
        return render(request, "hub/signup.html", {'form': form})
    
    elif request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():

            # Catch invalid repeat password
            if form.cleaned_data["password"]  != form.cleaned_data["repeat_password"]:
                return render(request, "hub/signup.html", {"form": form, "error_message": "The passwords don't match."})
            
            # Create the user. If the username is already taken, return an error stating it
            try:
                auth_user = AuthUser.objects.create_user(form.cleaned_data["username"], form.cleaned_data["email"], form.cleaned_data["password"])
            except IntegrityError:
                return render(request, "hub/signup.html", {"form": form, "error_message": "The username is already taken."})
            else:
                # If the auth_user was created, also create out user model
                User.objects.create(auth_user=auth_user)

            # If everything was successful return to the hub
            return HttpResponseRedirect("/login")
        else:
            # If something is wrong in the valid, check what it is and return a corresponding error
            return render(request, "hub/signup.html", {"form": form, "error_message": "There is a problem in the form!"})

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")

