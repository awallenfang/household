from django.test import TestCase
from django.contrib.auth.models import User as AuthUser

from space.models import SharedSpace
from hub.models import User
from .models import Todo






# Create your tests here.
class TodosTest(TestCase):
    def create_random_users(self, n) -> list[User]:
        users = []
        for i in range(n):
            auth_user = AuthUser.objects.create(username=str(i), password="a")
            user = User.objects.create(auth_user=auth_user)

            users.append(user)

        return users


    def create_test_todos(self, n):
        auth_user = AuthUser.objects.create(username="a", password="a")
        user = User.objects.create(auth_user=auth_user)
        space = SharedSpace.create_space("test", user)
        for _ in range(n):
            Todo.create_in_space(space)
    
    def create_single_todo(self) -> Todo:
        auth_user = AuthUser.objects.create(username="a", password="a")
        user = User.objects.create(auth_user=auth_user)
        space = SharedSpace.create_space("test", user)

        todo = Todo.create_in_space(space)

        return todo

    def test_creation(self):
        self.create_test_todos(10)
        todos = Todo.objects.all()
        self.assertEqual(len(todos), 10)

        last_todo = todos.order_by('-position')[0]
        self.assertEqual(last_todo.position, 9)

    def test_reordering(self):
        self.create_test_todos(10)
        left_todo = Todo.objects.get(position = 0)
        left_todo.reorder(7,8)
        self.assertEqual(left_todo.position, 8)

        left_todo.reorder(-1,0)
        self.assertEqual(left_todo.position, 0)

    def test_recurrency(self):
        todo = self.create_single_todo()
        users = self.create_random_users(3)

        todo.make_recurrent(users)

        self.assertEqual(users[0], todo.get_currently_assigned_user())
        self.assertEqual(users[1], todo.get_next_assigned_user())
    
    def test_empty_recurrency(self):
        todo = self.create_single_todo()
        users = self.create_random_users(3)
        users[1] = None

        todo.make_recurrent(users)

        self.assertEqual(users[0], todo.get_currently_assigned_user())
        self.assertEqual(None, todo.get_next_assigned_user())
