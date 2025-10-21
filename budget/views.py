from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView
from django.forms import inlineformset_factory
from .models import BudgetWeekList, BudgetWeekListItem

# Create your views here.
class WeeklyDashboard(TemplateView):
    template_name = "budget/dashboard.html"

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context["week"] = BudgetWeekList.get_current_list()
        context["current_form"] = inlineformset_factory(BudgetWeekList, BudgetWeekListItem, fields=["title", "cost", "cleared", "paid_by"], extra=3, can_delete=True)(instance=context["week"])
        return context