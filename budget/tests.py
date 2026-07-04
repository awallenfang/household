from decimal import Decimal
from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpRequest
from django.utils import translation
from django.utils.timezone import now

from space.models import SharedSpace
from hub.models import Profile
from .models import BudgetWeekList, BudgetWeekListItem


class BaseTest(TestCase):
    def create_user(self, name="testuser", password="pass"):
        auth_user = User.objects.create_user(username=name, password=password)
        return Profile.objects.create(user=auth_user)

    def create_space_and_user(self):
        user = self.create_user()
        space = SharedSpace.create_space("test space", user)
        return user, space

    def activate_language(self):
        translation.activate("en")

    def reverse(self, name, args=None, kwargs=None):
        self.activate_language()
        return reverse(name, args=args, kwargs=kwargs)


# ==============================================================================
# Model Tests
# ==============================================================================

class BudgetWeekListModelTest(BaseTest):
    def test_create_week_list(self):
        user, space = self.create_space_and_user()
        monday = now().date() - timedelta(days=now().date().weekday())
        week = BudgetWeekList.objects.create(week=monday, space=space)
        self.assertEqual(week.space, space)
        self.assertEqual(week.week, monday)

    def test_get_current_list_creates_if_missing(self):
        user, space = self.create_space_and_user()
        request = HttpRequest()
        request.user = user.user
        user.selected_space = space
        user.save()
        week = BudgetWeekList.get_current_list(request)
        self.assertIsNotNone(week)
        self.assertEqual(week.space, space)

    def test_get_current_list_returns_existing(self):
        user, space = self.create_space_and_user()
        monday = now().date() - timedelta(days=now().date().weekday())
        existing = BudgetWeekList.objects.create(week=monday, space=space)
        request = HttpRequest()
        request.user = user.user
        user.selected_space = space
        user.save()
        week = BudgetWeekList.get_current_list(request)
        self.assertEqual(week.id, existing.id)

    def test_get_list_from_date(self):
        user, space = self.create_space_and_user()
        a_date = date(2026, 6, 15)  # Monday
        request = HttpRequest()
        request.user = user.user
        user.selected_space = space
        user.save()
        week = BudgetWeekList.get_list_from_date(request, a_date)
        self.assertEqual(week.week, a_date)
        self.assertEqual(week.space, space)

    def test_get_list_from_date_non_monday(self):
        user, space = self.create_space_and_user()
        wed = date(2026, 6, 17)  # Wednesday
        expected_monday = date(2026, 6, 15)
        request = HttpRequest()
        request.user = user.user
        user.selected_space = space
        user.save()
        week = BudgetWeekList.get_list_from_date(request, wed)
        self.assertEqual(week.week, expected_monday)


class BudgetWeekListItemModelTest(BaseTest):
    def setUp(self):
        self.user, self.space = self.create_space_and_user()
        monday = now().date() - timedelta(days=now().date().weekday())
        self.week = BudgetWeekList.objects.create(week=monday, space=self.space)

    def test_create_item(self):
        item = BudgetWeekListItem.objects.create(
            list=self.week, title="Groceries", cost=Decimal("50.00"), paid_by=self.user.user,
        )
        self.assertEqual(item.title, "Groceries")
        self.assertEqual(item.cost, Decimal("50.00"))
        self.assertFalse(item.cleared)
        self.assertEqual(item.paid_by, self.user.user)

    def test_create_item_without_paid_by(self):
        item = BudgetWeekListItem.objects.create(
            list=self.week, title="Open item", cost=Decimal("25.00"),
        )
        self.assertIsNone(item.paid_by)

    def test_create_item_without_title(self):
        item = BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("15.00"), paid_by=self.user.user,
        )
        self.assertEqual(item.title, None)


class GetSumTest(BaseTest):
    def setUp(self):
        self.user, self.space = self.create_space_and_user()
        self.other = self.create_user("other")
        monday = now().date() - timedelta(days=now().date().weekday())
        self.week = BudgetWeekList.objects.create(week=monday, space=self.space)

    def test_get_sum_empty(self):
        self.assertEqual(self.week.get_sum(), {})

    def test_get_sum_single_item(self):
        BudgetWeekListItem.objects.create(
            list=self.week, title="Food", cost=Decimal("30.00"), paid_by=self.user.user,
        )
        result = self.week.get_sum()
        self.assertEqual(result[self.user.user], Decimal("30.00"))

    def test_get_sum_open_item(self):
        BudgetWeekListItem.objects.create(
            list=self.week, title="Misc", cost=Decimal("15.00"),
        )
        result = self.week.get_sum()
        self.assertEqual(result["open"], Decimal("15.00"))

    def test_get_sum_multiple_items_same_user(self):
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("10.00"), paid_by=self.user.user,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("20.00"), paid_by=self.user.user,
        )
        result = self.week.get_sum()
        self.assertEqual(result[self.user.user], Decimal("30.00"))

    def test_get_sum_multiple_users(self):
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("10.00"), paid_by=self.user.user,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("25.00"), paid_by=self.other.user,
        )
        result = self.week.get_sum()
        self.assertEqual(result[self.user.user], Decimal("10.00"))
        self.assertEqual(result[self.other.user], Decimal("25.00"))

    def test_get_sum_cleared_items_excluded(self):
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("10.00"), paid_by=self.user.user, cleared=True,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("20.00"), paid_by=self.user.user,
        )
        result = self.week.get_sum()
        self.assertEqual(result[self.user.user], Decimal("20.00"))

    def test_get_sum_include_cleared(self):
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("10.00"), paid_by=self.user.user, cleared=True,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("20.00"), paid_by=self.user.user,
        )
        result = self.week.get_sum(include_cleared=True)
        self.assertEqual(result[self.user.user], Decimal("30.00"))

    def test_get_sum_mixed_open_and_assigned(self):
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("10.00"), paid_by=self.user.user,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("5.00"),
        )
        result = self.week.get_sum()
        self.assertEqual(result[self.user.user], Decimal("10.00"))
        self.assertEqual(result["open"], Decimal("5.00"))


class GetDistributionTest(BaseTest):
    def setUp(self):
        self.user, self.space = self.create_space_and_user()
        self.other = self.create_user("other")
        monday = now().date() - timedelta(days=now().date().weekday())
        self.week = BudgetWeekList.objects.create(week=monday, space=self.space)

    def test_get_distribution_empty(self):
        self.assertEqual(self.week.get_distribution(), {})

    def test_get_distribution_single_person_returns_empty(self):
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("30.00"), paid_by=self.user.user,
        )
        self.assertEqual(self.week.get_distribution(), {})

    def test_get_distribution_only_open_returns_empty(self):
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("30.00"),
        )
        self.assertEqual(self.week.get_distribution(), {})

    def test_get_distribution_two_people(self):
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("40.00"), paid_by=self.user.user,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("20.00"), paid_by=self.other.user,
        )
        dist = self.week.get_distribution()
        # total: 60, each owes 30. User paid 40 → gets 10 back. Other paid 20 → owes 10.
        # Other owes User 10.
        # User receives from Other: Other owes User 10
        self.assertIn(self.other.user, dist)
        self.assertEqual(dist[self.other.user], [(self.user.user, Decimal("10.00"))])

    def test_get_distribution_with_open_items(self):
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("30.00"), paid_by=self.user.user,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("10.00"), paid_by=self.other.user,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("20.00"),
        )
        dist = self.week.get_distribution()
        # named people: user (30), other (10) → sum=40, each owes 20
        # User paid 30 → gets 10 back. Other paid 10 → owes 10.
        # Other owes User 10.
        self.assertIn(self.other.user, dist)
        self.assertEqual(dist[self.other.user], [(self.user.user, Decimal("10.00"))])

    def test_get_distribution_three_people(self):
        third = self.create_user("third")
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("60.00"), paid_by=self.user.user,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("30.00"), paid_by=self.other.user,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("0.00"), paid_by=third.user,
        )
        dist = self.week.get_distribution()
        # named: user(60), other(30), third(0) → sum=90, each owes 30
        # User paid 60 → gets 30 back
        # Other paid 30 → owes 0? No, other paid 30, owes 30 → exactly even
        # Third paid 0 → owes 30
        # Third owes 30 (split to user and other?)
        # Rounding: each pays 60/3=20 to each other? No, that's not how it works.
        # people_sum: {user: 60, other: 30, third: 0}
        # each person owes total_per_person = others_sum / people_amt
        # For user: owes round(30/3,2)=10.00 to other, owes round(0/3,2)=0.00 to third
        # For other: owes round(60/3,2)=20.00 to user, owes round(0/3,2)=0.00 to third
        # For third: owes round(60/3,2)=20.00 to user, owes round(30/3,2)=10.00 to other
        # Net: user receives 20 from other? No...
        # 
        # Re-tracing sendings:
        # people_amt = 3
        # sendings[user] = [(other, 30/3=10), (third, 0/3=0)]
        # sendings[other] = [(user, 60/3=20), (third, 0/3=0)]
        # sendings[third] = [(user, 60/3=20), (other, 30/3=10)]
        #
        # Pair (user, other): forward=10, backward=20 → backward > forward → other sends 10 to user
        # Pair (user, third): forward=0, backward=20 → backward > forward → third sends 20 to user
        # Pair (other, third): forward=0, backward=10 → backward > forward → third sends 10 to other
        #
        # actual: other→user(10), third→user(20), third→other(10)
        self.assertIn(self.other.user, dist)
        self.assertIn(third.user, dist)
        self.assertEqual(dist[self.other.user], [(self.user.user, Decimal("10.00"))])
        self.assertEqual(dist[third.user], [(self.user.user, Decimal("20.00")), (self.other.user, Decimal("10.00"))])

    def test_get_distribution_cleared_excluded(self):
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("40.00"), paid_by=self.user.user, cleared=True,
        )
        BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("20.00"), paid_by=self.other.user,
        )
        dist = self.week.get_distribution()
        # only other's 20 is included, user's 40 is cleared
        # single person → empty distribution
        self.assertEqual(dist, {})

    def test_week_goal(self):
        self.week.week_goal = Decimal("500.00")
        self.week.save()
        self.assertEqual(self.week.week_goal, Decimal("500.00"))


class ClearItemsTest(BaseTest):
    def setUp(self):
        self.user, self.space = self.create_space_and_user()
        monday = now().date() - timedelta(days=now().date().weekday())
        self.week = BudgetWeekList.objects.create(week=monday, space=self.space)

    def test_mark_item_cleared(self):
        item = BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("50.00"), paid_by=self.user.user,
        )
        self.assertFalse(item.cleared)
        item.cleared = True
        item.save()
        self.assertTrue(item.cleared)

    def test_mark_all_cleared(self):
        for _ in range(3):
            BudgetWeekListItem.objects.create(
                list=self.week, cost=Decimal("10.00"), paid_by=self.user.user,
            )
        for item in self.week.week_items.all():
            item.cleared = True
            item.save()
        self.assertEqual(self.week.get_sum(), {})


# ==============================================================================
# View Tests
# ==============================================================================

class DashboardViewTest(BaseTest):
    def test_dashboard_requires_login(self):
        response = self.client.get(self.reverse("budget:budget_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_requires_space(self):
        user = self.create_user()
        self.client.force_login(user.user)
        response = self.client.get(self.reverse("budget:budget_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_renders(self):
        user, space = self.create_space_and_user()
        user.selected_space = space
        user.spaces.add(space)
        user.save()
        self.client.force_login(user.user)
        response = self.client.get(self.reverse("budget:budget_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Budget")
        self.assertContains(response, "Summary")

    def test_dashboard_shows_outstanding_sum(self):
        user, space = self.create_space_and_user()
        user.selected_space = space
        user.spaces.add(space)
        user.save()
        self.client.force_login(user.user)

        monday = now().date() - timedelta(days=now().date().weekday())
        week = BudgetWeekList.objects.create(week=monday, space=space)
        BudgetWeekListItem.objects.create(
            list=week, cost=Decimal("42.50"), paid_by=user.user,
        )

        response = self.client.get(self.reverse("budget:budget_dashboard"))
        self.assertContains(response, "42.50")

    def test_dashboard_shows_distribution(self):
        user, space = self.create_space_and_user()
        other = self.create_user("other")
        user.selected_space = space
        user.spaces.add(space)
        other.spaces.add(space)
        user.save()

        self.client.force_login(user.user)

        monday = now().date() - timedelta(days=now().date().weekday())
        week = BudgetWeekList.objects.create(week=monday, space=space)
        BudgetWeekListItem.objects.create(
            list=week, cost=Decimal("40.00"), paid_by=user.user,
        )
        BudgetWeekListItem.objects.create(
            list=week, cost=Decimal("20.00"), paid_by=other.user,
        )

        response = self.client.get(self.reverse("budget:budget_dashboard"))
        self.assertContains(response, "testuser")
        self.assertContains(response, "other")


class CreateEntryViewTest(BaseTest):
    def setUp(self):
        self.user, self.space = self.create_space_and_user()
        self.user.selected_space = self.space
        self.user.spaces.add(self.space)
        self.user.save()
        self.client.force_login(self.user.user)
        self.monday = now().date() - timedelta(days=now().date().weekday())
        self.week = BudgetWeekList.objects.create(week=self.monday, space=self.space)

    def test_add_single_entry_with_minimal_total_forms(self):
        """Submit with TOTAL_FORMS=1 so only one form is validated."""
        response = self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "1",
            "week_items-INITIAL_FORMS": "0",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "week_items-0-title": "Groceries",
            "week_items-0-cost": "50.00",
            "week_items-0-paid_by": str(self.user.user.id),
        })
        self.assertEqual(response.status_code, 200)
        items = BudgetWeekListItem.objects.filter(list=self.week)
        self.assertEqual(items.count(), 1)
        self.assertEqual(items[0].title, "Groceries")
        self.assertEqual(items[0].cost, Decimal("50.00"))
        self.assertEqual(items[0].paid_by, self.user.user)

    def test_add_multiple_entries(self):
        response = self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "2",
            "week_items-INITIAL_FORMS": "0",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "week_items-0-title": "Food",
            "week_items-0-cost": "30.00",
            "week_items-0-paid_by": str(self.user.user.id),
            "week_items-1-title": "Drinks",
            "week_items-1-cost": "15.00",
            "week_items-1-paid_by": str(self.user.user.id),
        })
        self.assertEqual(response.status_code, 200)
        items = BudgetWeekListItem.objects.filter(list=self.week)
        self.assertEqual(items.count(), 2)

    def test_add_entry_with_open_paid_by(self):
        """Entry with no paid_by should be treated as 'open'."""
        response = self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "1",
            "week_items-INITIAL_FORMS": "0",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "week_items-0-title": "Misc",
            "week_items-0-cost": "12.50",
        })
        self.assertEqual(response.status_code, 200)
        items = BudgetWeekListItem.objects.filter(list=self.week)
        self.assertEqual(items.count(), 1)
        self.assertIsNone(items[0].paid_by)

    def test_entry_cost_required(self):
        """Submitting without cost should not save."""
        response = self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "1",
            "week_items-INITIAL_FORMS": "0",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "week_items-0-title": "No cost",
            "week_items-0-cost": "",
            "week_items-0-paid_by": str(self.user.user.id),
        })
        items = BudgetWeekListItem.objects.filter(list=self.week)
        self.assertEqual(items.count(), 0)

    def test_empty_extra_forms_are_skipped(self):
        """
        When the browser sends TOTAL_FORMS=5 (as rendered by extra=5),
        the empty extra forms with pre-filled paid_by should be skipped
        and only the filled form should be saved.
        """
        response = self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "5",
            "week_items-INITIAL_FORMS": "0",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "week_items-0-title": "Groceries",
            "week_items-0-cost": "50.00",
            "week_items-0-paid_by": str(self.user.user.id),
            "week_items-1-title": "",
            "week_items-1-cost": "",
            "week_items-1-paid_by": str(self.user.user.id),
            "week_items-2-title": "",
            "week_items-2-cost": "",
            "week_items-2-paid_by": str(self.user.user.id),
            "week_items-3-title": "",
            "week_items-3-cost": "",
            "week_items-3-paid_by": str(self.user.user.id),
            "week_items-4-title": "",
            "week_items-4-cost": "",
            "week_items-4-paid_by": str(self.user.user.id),
        })
        self.assertEqual(response.status_code, 200)
        items = BudgetWeekListItem.objects.filter(list=self.week)
        self.assertEqual(items.count(), 1)

    def test_added_form_does_not_override_existing(self):
        """
        Simulates clicking 'Add' (TOTAL_FORMS=6). The original form's data
        must be preserved despite the extra empty form in the submission.

        Includes all fields the browser would send: visible inputs,
        hidden id/list fields (inside <tbody> but outside <tr>),
        and the submit button.
        """
        uid = str(self.user.user.id)
        wid = str(self.week.pk)
        # First GET to create the week through the view, then POST
        self.client.get(self.reverse("budget:budget_dashboard"))
        response = self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "6",
            "week_items-INITIAL_FORMS": "0",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "week_items-0-title": "Groceries",
            "week_items-0-cost": "50.00",
            "week_items-0-cleared": "",
            "week_items-0-paid_by": uid,
            "week_items-0-id": "",
            "week_items-0-list": wid,
            "week_items-1-title": "",
            "week_items-1-cost": "",
            "week_items-1-cleared": "",
            "week_items-1-paid_by": uid,
            "week_items-1-id": "",
            "week_items-1-list": wid,
            "week_items-2-title": "",
            "week_items-2-cost": "",
            "week_items-2-cleared": "",
            "week_items-2-paid_by": uid,
            "week_items-2-id": "",
            "week_items-2-list": wid,
            "week_items-3-title": "",
            "week_items-3-cost": "",
            "week_items-3-cleared": "",
            "week_items-3-paid_by": uid,
            "week_items-3-id": "",
            "week_items-3-list": wid,
            "week_items-4-title": "",
            "week_items-4-cost": "",
            "week_items-4-cleared": "",
            "week_items-4-paid_by": uid,
            "week_items-4-id": "",
            "week_items-4-list": wid,
            # Form 5 was added via cloneMore — no hidden id/list
            "week_items-5-title": "",
            "week_items-5-cost": "",
            "week_items-5-cleared": "",
            "week_items-5-paid_by": uid,
            "submit_week": "Save week",
        })
        self.assertEqual(response.status_code, 200)
        items = BudgetWeekListItem.objects.filter(list=self.week)
        self.assertEqual(items.count(), 1)
        item = items.first()
        self.assertEqual(item.title, "Groceries")
        self.assertEqual(item.cost, Decimal("50.00"))


class PaidWeekViewTest(BaseTest):
    def setUp(self):
        self.user, self.space = self.create_space_and_user()
        self.user.selected_space = self.space
        self.user.spaces.add(self.space)
        self.user.save()
        self.client.force_login(self.user.user)
        monday = now().date() - timedelta(days=now().date().weekday())
        self.week = BudgetWeekList.objects.create(week=monday, space=self.space)
        for _ in range(3):
            BudgetWeekListItem.objects.create(
                list=self.week, cost=Decimal("10.00"), paid_by=self.user.user,
            )

    def test_paid_week_clears_all_items(self):
        response = self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "5",
            "week_items-INITIAL_FORMS": "0",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "paid_week": "All has been paid",
        })
        self.assertEqual(response.status_code, 200)
        for item in self.week.week_items.all():
            self.assertTrue(item.cleared)

    def test_paid_week_clears_even_when_forms_invalid(self):
        """The paid_week logic should run regardless of form validity."""
        response = self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "1",
            "week_items-INITIAL_FORMS": "0",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "week_items-0-cost": "",  # invalid: missing cost
            "paid_week": "All has been paid",
        })
        self.assertEqual(response.status_code, 200)
        for item in self.week.week_items.all():
            self.assertTrue(item.cleared)

    def test_outstanding_sum_zero_after_paid_week(self):
        self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "5",
            "week_items-INITIAL_FORMS": "0",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "paid_week": "All has been paid",
        })
        self.assertEqual(self.week.get_sum(), {})


class WeekGoalViewTest(BaseTest):
    def setUp(self):
        self.user, self.space = self.create_space_and_user()
        self.user.selected_space = self.space
        self.user.spaces.add(self.space)
        self.user.save()
        self.client.force_login(self.user.user)
        monday = now().date() - timedelta(days=now().date().weekday())
        self.week = BudgetWeekList.objects.create(week=monday, space=self.space)

    def test_set_week_goal(self):
        response = self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "0",
            "week_items-INITIAL_FORMS": "0",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "submit_week": "Save week",
            "week_goal": "500.00",
        })
        self.assertEqual(response.status_code, 200)
        self.week.refresh_from_db()
        self.assertEqual(self.week.week_goal, Decimal("500.00"))


class DeleteEntryViewTest(BaseTest):
    def setUp(self):
        self.user, self.space = self.create_space_and_user()
        self.user.selected_space = self.space
        self.user.spaces.add(self.space)
        self.user.save()
        self.client.force_login(self.user.user)
        monday = now().date() - timedelta(days=now().date().weekday())
        self.week = BudgetWeekList.objects.create(week=monday, space=self.space)
        self.item = BudgetWeekListItem.objects.create(
            list=self.week, cost=Decimal("25.00"), paid_by=self.user.user,
        )

    def test_delete_entry(self):
        """Submit with DELETE=on and the correct TOTAL/INITIAL forms count."""
        response = self.client.post(self.reverse("budget:budget_dashboard"), {
            "week_items-TOTAL_FORMS": "1",
            "week_items-INITIAL_FORMS": "1",
            "week_items-MIN_NUM_FORMS": "0",
            "week_items-MAX_NUM_FORMS": "1000",
            "week_items-0-id": str(self.item.id),
            "week_items-0-title": self.item.title or "",
            "week_items-0-cost": str(self.item.cost),
            "week_items-0-paid_by": str(self.user.user.id),
            "week_items-0-DELETE": "on",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(BudgetWeekListItem.objects.filter(id=self.item.id).exists())


class HubBudgetBoxTest(BaseTest):
    """Tests for the budget data shown on the hub page."""

    def test_hub_shows_budget_data(self):
        from hub.views import hub
        user, space = self.create_space_and_user()
        user.selected_space = space
        user.spaces.add(space)
        user.save()
        self.client.force_login(user.user)

        monday = now().date() - timedelta(days=now().date().weekday())
        week = BudgetWeekList.objects.create(week=monday, space=space)
        BudgetWeekListItem.objects.create(
            list=week, cost=Decimal("99.00"), paid_by=user.user,
        )

        response = self.client.get(self.reverse("hub:hub"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "99.00")
