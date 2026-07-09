from .forms import BudgetListEntryForm
from django.shortcuts import render
from hub.models import Profile


def create_budget_form(request):
    profile = Profile.objects.get(user=request.user)
    space = profile.selected_space
    form = BudgetListEntryForm(initial={"paid_by": request.user})
    from django.contrib.auth.models import User
    form.fields["paid_by"].queryset = User.objects.filter(profile__spaces=space)
    return render(request, "budget/partials/budget_entry.html", {"form": form})
