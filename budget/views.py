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
from hub.mixins import HTMXMixin
from .renderers import create_budget_form

@method_decorator(login_required, name='dispatch')
@method_decorator(space_required, name='dispatch')
class WeeklyDashboard(HTMXMixin, TemplateView):
    template_name = "budget/dashboard.html"
    partials = {
        "add_form": create_budget_form
    }

    def get_formset(self, data=None, instance=None, total=None):
        if total is None:
            total = 5
        return inlineformset_factory(
            BudgetWeekList, BudgetWeekListItem, BudgetListEntryForm,
            extra=5, can_delete=True
        )(
            data, instance=instance,
            initial=[{"paid_by": self.request.user} for _ in range(total)]
        )

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        user = Profile.objects.get(user=self.request.user)
        user_spaces = user.get_spaces
        selected_space = user.selected_space
        context.update({
            'user_spaces': user_spaces,
            'selected_space': selected_space
        })
        context["week"] = BudgetWeekList.get_current_list(self.request)

        formset = kwargs.get("formset")
        if formset is not None:
            context["current_form"] = formset
        else:
            context["current_form"] = self.get_formset(instance=context["week"])

        context["helper"] = BudgetListEntryFormHelper()
        people_sum = context["week"].get_sum()
        context["people_sum"] = people_sum
        context["outstanding_sum"] = sum(people_sum.values())
        context["week_form"] = kwargs.get(
            "budget_form",
            BudgetListForm(instance=context["week"])
        )

        context["form_errors"] = kwargs.get("form_errors", False)

        return context

    def post(self, request, *args, **kwargs):
        week = BudgetWeekList.get_current_list(self.request)
        total = int(request.POST.get("week_items-TOTAL_FORMS", 5))
        formset = self.get_formset(data=request.POST, instance=week, total=total)
        budget_form = BudgetListForm(request.POST, instance=week)

        form_errored = False

        if formset.is_valid() and budget_form.is_valid():
            formset.save()
            budget_form.save()
        else:
            form_errored = True

        if "paid_week" in request.POST:
            for item in week.week_items.all():
                item.cleared = True
                item.save()

        return render(request, "budget/dashboard.html", self.get_context_data(
            formset=formset if form_errored else None,
            budget_form=budget_form if form_errored else None,
            form_errors=form_errored
        ))
