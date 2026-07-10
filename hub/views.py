from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils import translation
from django.utils.timezone import now
from django.views.generic import CreateView
from datetime import timedelta
from .models import Profile
from todos.models import Todo
from budget.models import BudgetWeekList

@login_required
def hub(request):
    user = Profile.objects.get(user = request.user)
        
    user_spaces = user.get_spaces
    selected_space = user.selected_space

    open_todo_amt = Todo.objects.filter(space = selected_space, done = False).count()
    closed_todo_amt = Todo.objects.filter(space = selected_space, done = True).count()
    assigned_todo_amt = Todo.objects.filter(space = selected_space, done = False, assigned_user = user).count()
    total_todo_amt = open_todo_amt + closed_todo_amt

    if selected_space:
        monday = now().date() - timedelta(days=now().date().weekday())
        week_list = BudgetWeekList.objects.filter(week=monday, space=selected_space).first()
        if week_list:
            budget_people_sum = week_list.get_sum()
            budget_outstanding_sum = sum(budget_people_sum.values())
        else:
            week_list = None
            budget_people_sum = {}
            budget_outstanding_sum = 0
    else:
        week_list = None
        budget_people_sum = {}
        budget_outstanding_sum = 0

    context = {"user_spaces": user_spaces, 
    "selected_space": selected_space,
    "open_todo_amt": open_todo_amt,
    "closed_todo_amt": closed_todo_amt,
    "open_assigned_todo_amt": assigned_todo_amt,
    "open_todos_due": 42,
    "total_todo_amt": total_todo_amt,
    "gradient_deg": int((closed_todo_amt/total_todo_amt)*360) if total_todo_amt else 0,
    "gradient_percent": int((closed_todo_amt/total_todo_amt)*100) if total_todo_amt else 0,
    "budget_week": week_list,
    "budget_people_sum": budget_people_sum,
    "budget_outstanding_sum": budget_outstanding_sum,}
    return render(request, 
                    "hub/hub.html", 
                    context)
    
class SignupView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        return response

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")

def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        if language:
            translation.activate(language)
