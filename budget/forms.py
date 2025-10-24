from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms import layout
from .models import BudgetWeekListItem, BudgetWeekList
from django.utils.translation import gettext_lazy as _

class   BudgetListForm(forms.ModelForm):
    class Meta:
        model = BudgetWeekList
        fields = ["week_goal"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = layout.Layout(
            layout.Column(
                layout.Column(
                    "week_goal"
                ),
                layout.Row(
                    layout.Column(
                        layout.Submit("submit_week", _("Save week")),
                    ),
                    layout.Column(
                        layout.Submit("paid_week", _("All has been paid")),
                    )
                )
            ),
        )
    

class BudgetListEntryForm(forms.ModelForm):
    class Meta:
        model = BudgetWeekListItem
        fields = ["title", "cost", "cleared", "paid_by"]

class BudgetListEntryFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.form_tag = False
        self.layout = layout.Layout(
            layout.Row(
                layout.Column("title"), layout.Column("cost"), layout.Column("paid_by"), layout.Column("cleared"),
                css_class="d-flex flex-row justify-content-between align-items-center"
            )
        )

        self.add_input(layout.Submit("submit", _("Save")))