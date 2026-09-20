from datetime import date
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
        profile = Profile.objects.get(user=self.request.user)
        space = profile.selected_space
        FormSet = inlineformset_factory(
            BudgetWeekList, BudgetWeekListItem, BudgetListEntryForm,
            extra=5, can_delete=True
        )
        form_kwargs = {"space": space} if space is not None else {}
        return FormSet(
            data, instance=instance,
            initial=[{"paid_by": self.request.user} for _ in range(total)],
            form_kwargs=form_kwargs,
        )

    def get_week_for_request(self):
        year, month, day = (
            self.kwargs.get("year"),
            self.kwargs.get("month"),
            self.kwargs.get("day"),
        )
        if year and month and day:
            try:
                return BudgetWeekList.peek_list_from_date(
                    self.request, date(year, month, day)
                )
            except ValueError:
                pass
        return BudgetWeekList.peek_current_list(self.request)

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        user = Profile.objects.get(user=self.request.user)
        user_spaces = user.get_spaces
        selected_space = user.selected_space
        context.update({
            'user_spaces': user_spaces,
            'selected_space': selected_space
        })
        context["week"] = self.get_week_for_request()

        formset = kwargs.get("formset")
        if formset is not None:
            context["current_form"] = formset
        elif context["week"].pk is None:
            # No row yet and GET must not create one: render blank forms.
            # (An unsaved instance would crash week_items / inline formsets.)
            context["current_form"] = self.get_formset(instance=None)
        else:
            context["current_form"] = self.get_formset(instance=context["week"])

        context["helper"] = BudgetListEntryFormHelper()
        if context["week"].pk is None:
            people_sum = {}
        else:
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
        try:
            total = int(request.POST.get("week_items-TOTAL_FORMS", 5))
        except (TypeError, ValueError):
            total = 5
        # Bound formset size: an unbounded TOTAL_FORMS is a trivial CPU/memory DoS.
        total = max(1, min(total, 50))
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
