from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms import layout

from .models import BudgetWeekListItem, BudgetWeekList

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["cleared"].label = False
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_tag = False
        self.helper.layout = layout.Layout(
            layout.HTML("<tr>"),            
            layout.HTML("<td>"),
            layout.Field("cleared", wrapper_class='d-flex align-items-center justify-content-center'),
            layout.HTML("</td>"),
            layout.HTML("<td>"),
            "title", 
            layout.HTML("</td>"),
            layout.HTML("<td>"),
            "cost", 
            layout.HTML("</td>"),
            layout.HTML("<td>"),
            "paid_by", 
            layout.HTML("</td>"),
            layout.HTML("</tr>"),            
        )


class BudgetListEntryFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.form_show_labels = False
        self.form_tag = False
        self.layout = layout.Layout(
            layout.HTML("<tr>"),            
            layout.HTML("<td>"),
            layout.Field("cleared", wrapper_class='d-flex align-items-center justify-content-center'),
            layout.HTML("</td>"),
            layout.HTML("<td>"),
            "title", 
            layout.HTML("</td>"),
            layout.HTML("<td>"),
            "cost", 
            layout.HTML("</td>"),
            layout.HTML("<td>"),
            "paid_by", 
            layout.HTML("</td>"),
            layout.HTML("</tr>"),            
        )

