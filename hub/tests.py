from django.test import TestCase
from django.contrib.auth.models import User as AuthUser
from space.models import InvalidTokenError, SharedSpace
from .models import User
# Create your tests here.
class UserTest(TestCase):
    def create_testuser(self, name):
        auth_user = AuthUser.objects.create_user(username=name, password="test")
        user = User.objects.create(auth_user=auth_user)
        return user

    def test_user_creation(self):
        user = self.create_testuser("test1")
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.__str__(), "User: test1")

class SharedSpaceTest(TestCase):
    def create_testspace(self):
        user = self.create_testuser("test2")
        return SharedSpace.create_space("test space", user)
    
    def create_testuser(self, name):
        auth_user = AuthUser.objects.create_user(username=name, password="test")
        user = User.objects.create(auth_user=auth_user)
        return user
    
    def test_space_creation(self):
        space = self.create_testspace()
        self.assertTrue(space.invite_token != "")
        self.assertEqual(space.name, "test space")
        self.assertEqual(space.__str__(), "Shared Space: test space")

    def test_space_user_connection(self):
        space = self.create_testspace()
        user = self.create_testuser("test3")

        SharedSpace.join(user, space.invite_token)

        self.assertTrue(user.spaces.contains(space))
        with self.assertRaises(InvalidTokenError):
            SharedSpace.join(user, "")
