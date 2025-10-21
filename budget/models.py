from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import localtime, now
from django.contrib.auth.models import User


from datetime import datetime, timedelta
from datetime import date
from space.models import SharedSpace



# Create your models here.

class BudgetWeekList(models.Model):
    week = models.DateField(verbose_name=_("Week"))
    week_goal = models.DecimalField(_("Weekly goal"), decimal_places=2, max_digits=8, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @staticmethod
    def get_current_list():
        date = now().date()
        monday = date - timedelta(days=date.weekday())
        return BudgetWeekList.objects.get_or_create(week=monday)[0]

    @staticmethod
    def get_list_from_date(date: date):
        monday = date - timedelta(days=date.weekday())
        return BudgetWeekList.objects.get_or_create(week=monday)[0]


class BudgetWeekListItem(models.Model):
    list = models.ForeignKey(BudgetWeekList, verbose_name=_("Weekly budget"), on_delete=models.CASCADE)
    title = models.CharField(_("Title"), max_length=255, blank=True, null=True)
    cost = models.DecimalField(_("Cost"), decimal_places=2, max_digits=8, blank=False, null=False)
    cleared = models.BooleanField(_("Cost cleared"), default=False)
    paid_by = models.ForeignKey(User, verbose_name=_("Paid by"), on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)