from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import localtime, now
from django.contrib.auth.models import User
from hub.models import Profile
from decimal import Decimal

from datetime import datetime, timedelta
from datetime import date
from space.models import SharedSpace



# Create your models here.

class BudgetWeekList(models.Model):
    space = models.ForeignKey(SharedSpace, verbose_name=("Space"), on_delete=models.CASCADE, null=True, blank=True)
    week = models.DateField(verbose_name=_("Week"))
    week_goal = models.DecimalField(_("Weekly goal"), decimal_places=2, max_digits=8, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @staticmethod
    def get_current_list(request):
        user = Profile.objects.get(user = request.user)
        selected_space = user.selected_space

        date = now().date()
        monday = date - timedelta(days=date.weekday())
        return BudgetWeekList.objects.get_or_create(week=monday, space = selected_space)[0]

    @staticmethod
    def get_list_from_date(request, date: date):
        monday = date - timedelta(days=date.weekday())
        return BudgetWeekList.objects.get_or_create(week=monday)[0]

    def get_sum(self, include_cleared = False):
        people_sum = {}
        for item in self.week_items.all():
            if not include_cleared and item.cleared:
                continue
            if not item.paid_by:
                if "open" not in people_sum.keys():
                    people_sum["open"] = item.cost
                else:
                    people_sum["open"] += item.cost
                continue
        
            if item.paid_by not in people_sum.keys():
                people_sum[item.paid_by] = item.cost
            else:
                people_sum[item.paid_by] += item.cost
        return people_sum

    def get_distribution(self):
        """
        Returns what everyone gets from everyone else per person.
        """
        people_sum = self.get_sum()
        distribution = {}
        people_amt = len(people_sum)
        if "open" in people_sum.keys():
            people_amt -= 1

        people = list(people_sum.keys())
        if "open" in people:
            people.remove("open")
        
        sendings = {}
        # Set up sendings
        for p in people:
            own_amt = people_sum[p]
            sendings[p] = []
            for o_p in people:
                if o_p == p:
                    continue
                sendings[p].append((o_p, round(people_sum[o_p] / Decimal(people_amt), ndigits=2)))

        actual_sendings = {p:[] for p in sendings.keys()}
        for i,p in enumerate(people):
            for j in range(i+1, len(people)):
                o_p = people[j]
                forward_sendings = list(filter(lambda send: send[0] == o_p, sendings[p]))
                backward_sendings = list(filter(lambda send: send[0] == p, sendings[o_p]))

                forward = 0
                if len(forward_sendings)>0:
                    forward = forward_sendings[0][1]
                backward = 0
                if len(backward_sendings)>0:
                    backward = backward_sendings[0][1]

                if forward > backward:
                    actual_sendings[p].append((o_p, forward - backward)) 
                elif forward < backward:
                    actual_sendings[o_p].append((p, backward - forward)) 

        to_delete = []
        for p in actual_sendings.keys():
            if len(actual_sendings[p]) == 0:
                to_delete.append(p)

        for p in to_delete:
            del actual_sendings[p]
        return actual_sendings

class BudgetWeekListItem(models.Model):
    list = models.ForeignKey(BudgetWeekList, verbose_name=_("Weekly budget"), on_delete=models.CASCADE, related_name="week_items")
    title = models.CharField(_("Title"), max_length=255, blank=True, null=True)
    cost = models.DecimalField(_("Cost"), decimal_places=2, max_digits=8, blank=False, null=False)
    cleared = models.BooleanField(_("Cost cleared"), default=False)
    paid_by = models.ForeignKey(User, verbose_name=_("Paid by"), on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)