from .forms import BudgetListEntryForm, BudgetListEntryFormHelper
from django.shortcuts import render
def create_budget_form(request):
    form = BudgetListEntryForm(data = {"paid_by": request.user})
    helper = BudgetListEntryFormHelper()
    print(form.helper)


    return render(request, "budget/partials/budget_entry.html", {"form": form, "helper": helper})