from django.test import TestCase

from .models import Todo

# Create your tests here.
class TodosTest(TestCase):
    def create_test_todos(self, n):
        for _ in range(n):
            Todo.create_default()

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