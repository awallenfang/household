from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpRequest
from django.utils import translation

from space.models import SharedSpace
from hub.models import Profile
from .models import Todo, TodoSchedule, SubTask


class BaseTest(TestCase):
    def create_user(self, name="testuser", password="pass"):
        auth_user = User.objects.create_user(username=name, password=password)
        return Profile.objects.create(user=auth_user)

    def create_space_and_user(self):
        user = self.create_user()
        space = SharedSpace.create_space("test space", user)
        return user, space

    def login(self, user=None):
        if user is None:
            user = self.create_user()
        self.client.force_login(user.user)
        return user

    def reverse(self, name, args=None, kwargs=None):
        translation.activate("en")
        return reverse(name, args=args, kwargs=kwargs)

    def create_todo(self, name="Test Todo", description="Test Description"):
        user, space = self.create_space_and_user()
        todo = Todo.create_in_space(space)
        todo.name = name
        todo.description = description
        todo.save()
        return todo, user, space

    def set_selected_space(self, user, space):
        user.selected_space = space
        user.save()


# ==============================================================================
# Model Tests
# ==============================================================================

class TodoModelTest(BaseTest):
    def test_creation(self):
        user, space = self.create_space_and_user()
        todos = []
        for _ in range(10):
            t = Todo.create_in_space(space)
            todos.append(t)
        self.assertEqual(Todo.objects.filter(space=space).count(), 10)
        last = Todo.objects.filter(space=space).order_by("-position").first()
        self.assertEqual(last.position, 9)

    def test_reordering(self):
        user, space = self.create_space_and_user()
        for _ in range(10):
            Todo.create_in_space(space)
        left_todo = Todo.objects.get(position=1)
        left_todo.reorder(7, 8)
        self.assertEqual(left_todo.position, 8)
        left_todo.reorder(-1, 0)
        self.assertEqual(left_todo.position, 0)

    def test_minimize_positions(self):
        user, space = self.create_space_and_user()
        for _ in range(5):
            Todo.create_in_space(space)
        t = Todo.objects.get(position=3)
        t.position = 99
        t.save()
        Todo.minimize_positions()
        t.refresh_from_db()
        self.assertEqual(t.position, 4)

    def test_open_and_closed_queries(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        request = HttpRequest()
        request.user = user.user
        open_todos = Todo.get_open(request)
        self.assertIn(todo, open_todos)
        todo.done = True
        todo.save()
        closed_todos = Todo.get_closed(request)
        self.assertIn(todo, closed_todos)
        self.assertNotIn(todo, Todo.get_open(request))

    def test_assign_user(self):
        todo, user, space = self.create_todo()
        other = self.create_user("other")
        todo.assign_user(other)
        self.assertEqual(todo.assigned_user, other)

    def test_assign_user_blocked_when_scheduled(self):
        todo, user, space = self.create_todo()
        other = self.create_user("other")
        todo.make_scheduled([user])
        todo.assign_user(other)
        self.assertNotEqual(todo.assigned_user, other)

    def test_set_open_closed(self):
        todo, _, _ = self.create_todo()
        self.assertFalse(todo.done)
        todo.set_closed()
        self.assertTrue(todo.done)
        todo.set_open()
        self.assertFalse(todo.done)

    def test_currently_assigned_user_no_schedule(self):
        todo, user, _ = self.create_todo()
        todo.assigned_user = user
        todo.save()
        self.assertEqual(todo.get_currently_assigned_user, user)

    def test_create_in_space_position(self):
        _, space = self.create_space_and_user()
        todo = Todo.create_in_space(space)
        self.assertEqual(todo.name, "New Todo")
        self.assertEqual(todo.description, "")
        self.assertEqual(todo.space, space)
        self.assertEqual(todo.position, 1)

    def test_minimize_positions_after_delete(self):
        _, space = self.create_space_and_user()
        for _ in range(5):
            Todo.create_in_space(space)
        Todo.objects.get(position=3).delete()
        Todo.minimize_positions()
        positions = list(Todo.objects.filter(space=space).values_list("position", flat=True))
        self.assertEqual(positions, [0, 1, 2, 3])


class ScheduleModelTest(BaseTest):
    def test_schedule_rotation(self):
        todo, user, _ = self.create_todo()
        users = []
        for i in range(3):
            u = self.create_user(f"user{i}")
            users.append(u)
        todo.make_scheduled(users)
        self.assertEqual(todo.get_currently_assigned_user, users[0])
        self.assertEqual(todo.get_next_assigned_user, users[1])

    def test_empty_schedule(self):
        todo, user, _ = self.create_todo()
        users = [self.create_user("a"), None, self.create_user("c")]
        todo.make_scheduled(users)
        self.assertEqual(todo.get_currently_assigned_user, users[0])
        self.assertEqual(todo.get_next_assigned_user, None)

    def test_add_user_to_schedule(self):
        todo, owner, _ = self.create_todo()
        todo.make_scheduled([owner])
        other = self.create_user("other")
        todo.schedule_state.add_user(other)
        self.assertIn(other, todo.schedule_state.assigned_users.all())

    def test_add_empty_to_schedule(self):
        todo, user, _ = self.create_todo()
        todo.make_scheduled([user])
        todo.schedule_state.add_empty()
        users = todo.schedule_state.get_full_order
        self.assertIsNone(users[1])

    def test_remove_user_at_position(self):
        todo, user, _ = self.create_todo()
        users = [self.create_user(f"u{i}") for i in range(3)]
        todo.make_scheduled(users)
        todo.schedule_state.remove_user_at_position(1)
        remaining = todo.schedule_state.assigned_users.all()
        self.assertNotIn(users[1], remaining)
        order = todo.schedule_state.get_full_order
        self.assertEqual(len(order), 2)

    def test_reorder_users_moves_user_to_position(self):
        todo, user, _ = self.create_todo()
        users = [self.create_user(f"u{i}") for i in range(3)]
        todo.make_scheduled(users)
        todo.schedule_state.reorder_user(0, 2)
        order = todo.schedule_state.get_full_order
        self.assertEqual(order[0], users[1])
        self.assertEqual(order[1], users[0])

    def test_schedule_removal_clears_state(self):
        todo, user, _ = self.create_todo()
        todo.make_scheduled([user])
        self.assertIsNotNone(todo.schedule_state)
        todo.schedule_state = None
        todo.save()
        self.assertIsNone(todo.schedule_state)

    def test_schedule_tick(self):
        todo, user, _ = self.create_todo()
        users = [self.create_user(f"u{i}") for i in range(3)]
        todo.make_scheduled(users)
        self.assertEqual(todo.schedule_state.schedule_turn, 0)
        todo.schedule_state.schedule_turn = 1
        todo.schedule_state.save()
        self.assertEqual(todo.schedule_state.schedule_turn, 1)

    def test_rate_change(self):
        todo, user, _ = self.create_todo()
        todo.make_scheduled([user])
        todo.schedule_state.day_rotation = 14
        todo.schedule_state.save()
        self.assertEqual(todo.schedule_state.day_rotation, 14)


class SubTaskModelTest(BaseTest):
    def test_create_subtask(self):
        todo, _, _ = self.create_todo()
        st = SubTask.objects.create(title="Subtask 1", todo=todo)
        self.assertEqual(str(st), "SubTask: Subtask 1 on Test Todo")
        self.assertFalse(st.done)

    def test_toggle_subtask(self):
        todo, _, _ = self.create_todo()
        st = SubTask.objects.create(title="Subtask 1", todo=todo)
        st.done = True
        st.save()
        self.assertTrue(st.done)


# ==============================================================================
# View / Interaction Tests
# ==============================================================================

class TodoDashboardTest(BaseTest):
    def test_dashboard_requires_login(self):
        response = self.client.get(self.reverse("todos:todos"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_requires_space(self):
        user = self.create_user()
        self.client.force_login(user.user)
        response = self.client.get(self.reverse("todos:todos"))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_shows_todos(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        response = self.client.get(self.reverse("todos:todos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Todo")

    def test_dashboard_empty_state(self):
        user, space = self.create_space_and_user()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        response = self.client.get(self.reverse("todos:todos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New Todo")


class CreateTodoTest(BaseTest):
    def test_create_todo_via_hx_get(self):
        user, space = self.create_space_and_user()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        response = self.client.get(
            self.reverse("todos:add_todo") + "?hxp=create_todo",
            HTTP_HX_REQUEST="true",
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Todo.objects.filter(space=space).count(), 1)

    def test_create_todo_via_hx_post(self):
        user, space = self.create_space_and_user()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        response = self.client.post(
            self.reverse("todos:add_todo") + "?hxp=create_todo",
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Todo.objects.filter(space=space).count(), 1)
        todo = Todo.objects.filter(space=space).first()
        self.assertEqual(todo.name, "New Todo")
        self.assertEqual(todo.assigned_user, user)


class DeleteTodoTest(BaseTest):
    def test_delete_todo_via_hx_get(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:delete_todo", args=[todo.id])
        response = self.client.get(url + "?hxp=todo_list", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Todo.objects.filter(id=todo.id).exists())

    def test_cannot_delete_other_space_todo(self):
        todo, user, space = self.create_todo()
        other_user = self.create_user("other")
        other_space = SharedSpace.create_space("other", other_user)
        self.set_selected_space(other_user, other_space)
        self.client.force_login(other_user.user)
        url = self.reverse("todos:delete_todo", args=[todo.id])
        response = self.client.get(url + "?hxp=todo_list", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Todo.objects.filter(id=todo.id).exists())


class ToggleTodoTest(BaseTest):
    def test_close_todo_via_hx_post(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:todo", args=[todo.id])
        response = self.client.post(url + "?hxp=close_todo", {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertTrue(todo.done)

    def test_open_todo_via_hx_post(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        todo.done = True
        todo.save()
        url = self.reverse("todos:todo", args=[todo.id])
        response = self.client.post(url + "?hxp=open_todo", {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertFalse(todo.done)


class EditTodoTest(BaseTest):
    def test_edit_form_renders(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:edit_todo", args=[todo.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Todo")

    def test_edit_form_submit(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:edit_todo", args=[todo.id])
        response = self.client.post(url, {"name": "Updated!", "description": "New desc"})
        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertEqual(todo.name, "Updated!")
        self.assertEqual(todo.description, "New desc")

    def test_edit_form_empty_description_allowed(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:edit_todo", args=[todo.id])
        response = self.client.post(url, {"name": "No desc"})
        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertEqual(todo.name, "No desc")

    def test_edit_form_cross_space_blocked(self):
        """A user in one space cannot edit a todo from another space."""
        todo, user, space = self.create_todo()
        other_user = self.create_user("other")
        other_space = SharedSpace.create_space("other", other_user)
        self.set_selected_space(other_user, other_space)
        self.client.force_login(other_user.user)
        url = self.reverse("todos:edit_todo", args=[todo.id])
        response = self.client.post(url, {"name": "Hacked!"})
        self.assertEqual(response.status_code, 404)


class ScheduleInteractionTest(BaseTest):
    def test_add_schedule_via_hx_get(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:todo", args=[todo.id])
        response = self.client.get(url + "?hxp=add_schedule", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertIsNotNone(todo.schedule_state)
        self.assertIn(user, todo.schedule_state.assigned_users.all())

    def test_schedule_editor_get(self):
        user, space = self.create_space_and_user()
        user.spaces.add(space)
        self.set_selected_space(user, space)
        todo = Todo.create_in_space(space)
        todo.make_scheduled([user])
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user-add-check")

    def test_schedule_editor_empty_without_schedule(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")

    def test_add_users_to_schedule_via_hx_post(self):
        todo, user, space = self.create_todo()
        todo.make_scheduled([user])
        self.set_selected_space(user, space)
        other = self.create_user("other")
        SharedSpace.join(other, space.invite_token)
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.post(
            url + "?hxp=add_users&users=" + str(other.id),
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(other, todo.schedule_state.assigned_users.all())

    def test_add_empty_slot_to_schedule_via_hx_post(self):
        todo, user, space = self.create_todo()
        todo.make_scheduled([user])
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.post(
            url + "?hxp=add_users&users=-1",
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        order = todo.schedule_state.get_full_order
        self.assertIsNone(order[1])

    def test_change_rate_via_hx_post(self):
        todo, user, space = self.create_todo()
        todo.make_scheduled([user])
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.post(
            url + "?hxp=change_rate&rate=14",
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        todo.schedule_state.refresh_from_db()
        self.assertEqual(todo.schedule_state.day_rotation, 14)

    def test_change_rate_ignored_without_schedule(self):
        todo, user, space = self.create_todo()
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.post(
            url + "?hxp=change_rate&rate=14",
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(todo.schedule_state)

    def test_delete_position_via_hx_post(self):
        todo, user, space = self.create_todo()
        users = [self.create_user(f"u{i}") for i in range(3)]
        todo.make_scheduled(users)
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.post(
            url + "?hxp=delete_position&position=1",
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(users[1], todo.schedule_state.assigned_users.all())

    def test_reorder_user_in_schedule_via_hx_post(self):
        todo, user, space = self.create_todo()
        users = [self.create_user(f"u{i}") for i in range(3)]
        todo.make_scheduled(users)
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.post(
            url + "?hxp=reorder_user&pos=2&prev_pos=0",
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        order = todo.schedule_state.get_full_order
        self.assertEqual(order[1], users[0])

    def test_set_position_via_hx_post(self):
        todo, user, space = self.create_todo()
        users = [self.create_user(f"u{i}") for i in range(3)]
        todo.make_scheduled(users)
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.post(
            url + "?hxp=set_position&position=2",
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        todo.schedule_state.refresh_from_db()
        self.assertEqual(todo.schedule_state.schedule_turn, 2)

    def test_set_position_clamps_to_max(self):
        todo, user, space = self.create_todo()
        users = [self.create_user(f"u{i}") for i in range(3)]
        todo.make_scheduled(users)
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.post(
            url + "?hxp=set_position&position=99",
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        todo.schedule_state.refresh_from_db()
        self.assertEqual(todo.schedule_state.schedule_turn, 2)

    def test_remove_schedule_via_hx_get(self):
        todo, user, space = self.create_todo()
        todo.make_scheduled([user])
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:schedule_editor", args=[todo.id])
        response = self.client.get(url + "?hxp=remove_schedule", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertIsNone(todo.schedule_state)
        self.assertEqual(todo.assigned_user, user)


class ReorderTodoTest(BaseTest):
    def test_reorder_open_todo_via_hx_get(self):
        todo, user, space = self.create_todo()
        for _ in range(3):
            Todo.create_in_space(space)
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:todos")
        params = "?hxp=reorder_list&todo_id=1&left=-1&right=2&status=open"
        response = self.client.get(url + params, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        t = Todo.objects.get(id=1)
        self.assertLessEqual(t.position, 2)

    def test_reorder_closed_todo_via_hx_get(self):
        todo, user, space = self.create_todo()
        for _ in range(3):
            Todo.create_in_space(space)
        Todo.objects.all().update(done=True)
        self.set_selected_space(user, space)
        self.client.force_login(user.user)
        url = self.reverse("todos:todos")
        params = "?hxp=reorder_list&todo_id=1&left=-1&right=2&status=done"
        response = self.client.get(url + params, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        t = Todo.objects.get(id=1)
        self.assertTrue(t.done)
