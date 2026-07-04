from .forms import BudgetListEntryForm
from django.shortcuts import render


def create_budget_form(request):
    form = BudgetListEntryForm(initial={"paid_by": request.user})
    return render(request, "budget/partials/budget_entry.html", {"form": form})
