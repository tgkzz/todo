from django.test import TestCase
from django.contrib.auth.models import User
from .models import Todo
from django.db import DataError


# Create your tests here.
class TodoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )

        self.todo = Todo.objects.create(
            title="Test Todo",
            description="Test description",
            user=self.user
        )

    def test_todo_creation(self):
        self.assertEqual(self.todo.title, "Test Todo")
        self.assertEqual(self.todo.description, "Test description")
        self.assertEqual(self.todo.important, False)
        self.assertEqual(self.todo.user, self.user)

    def test_todo_string_representation(self):
        self.assertEqual(str(self.todo), "Test Todo")

    def test_todo_update(self):
        self.todo.title = "Updated Title"
        self.todo.save()
        updated_todo = Todo.objects.get(id=self.todo.id)
        self.assertEqual(updated_todo.title, "Updated Title")

    def test_todo_deletion(self):
        todo_id = self.todo.id
        self.todo.delete()
        with self.assertRaises(Todo.DoesNotExist):
            Todo.objects.get(id=todo_id)

    def test_todo_user_cascade_deletion(self):
        user_id = self.user.id
        self.user.delete()
        with self.assertRaises(Todo.DoesNotExist):
            Todo.objects.get(user_id=user_id)


class TodoDatabaseTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.todo1 = Todo.objects.create(
            title="First Todo",
            description="Test description",
            user=self.user
        )
        self.todo2 = Todo.objects.create(
            title="Important Todo",
            description="Another description",
            user=self.user,
            important=True
        )

    def test_todo_filter_by_user(self):
        todos_for_user = Todo.objects.filter(user=self.user)
        self.assertEqual(todos_for_user.count(), 2)
        self.assertIn(self.todo1, todos_for_user)
        self.assertIn(self.todo2, todos_for_user)

    def test_todo_filter_by_importance(self):
        important_todos = Todo.objects.filter(important=True)
        self.assertEqual(important_todos.count(), 1)
        self.assertIn(self.todo2, important_todos)

    def test_todo_ordering_by_creation(self):
        todos_ordered = Todo.objects.all().order_by('datecreated')
        self.assertEqual(todos_ordered[0], self.todo1)
        self.assertEqual(todos_ordered[1], self.todo2)

    def test_sql_injection(self):
        malicious_input = "'; DROP TABLE auth_user; --"
        Todo.objects.create(title=malicious_input, user=self.user)

        try:
            user_exists = User.objects.filter(username='testuser').exists()
            self.assertTrue(user_exists)
        except:
            self.fail("SQL injection test failed!")