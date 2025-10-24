from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView
from django.forms import inlineformset_factory
from .models import BudgetWeekList, BudgetWeekListItem
from .forms import BudgetListEntryForm, BudgetListEntryFormHelper, BudgetListForm
from hub.models import Profile
from django.contrib.auth.decorators import login_required
from hub.decorators import space_required
from django.utils.decorators import method_decorator

# Create your views here.
@method_decorator(login_required, name='dispatch')
@method_decorator(space_required, name='dispatch')
class WeeklyDashboard(TemplateView):
    template_name = "budget/dashboard.html"

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        user = Profile.objects.get(user = self.request.user)
        user_spaces = user.get_spaces
        selected_space = user.selected_space
        context.update({
            'user_spaces': user_spaces,
            'selected_space': selected_space
        })
        context["week"] = BudgetWeekList.get_current_list(self.request)
        context["current_form"] = inlineformset_factory(BudgetWeekList, BudgetWeekListItem, BudgetListEntryForm, extra=5, can_delete=True)(instance=context["week"])
        context["helper"] = BudgetListEntryFormHelper()
        people_sum = context["week"].get_sum()
        context["people_sum"] = people_sum
        context["outstanding_sum"] = sum(map(lambda k: people_sum[k], people_sum.keys()))
        context["week_form"] = BudgetListForm(instance = context["week"])
        return context

    def post(self, request, *args, **kwargs):
            
        week = BudgetWeekList.get_current_list(self.request)
        formset = inlineformset_factory(BudgetWeekList, BudgetWeekListItem, BudgetListEntryForm, extra=5, can_delete=True)(request.POST, instance = week)
        budget_form = BudgetListForm(request.POST, instance = week)

        if formset.is_valid() and budget_form.is_valid():
            formset.save()
            budget_form.save()
        
        if "paid_week" in request.POST:
            for item in week.week_items.all():
                item.cleared = True
                item.save()
        return render(request, "budget/dashboard.html", self.get_context_data(*args, **kwargs))