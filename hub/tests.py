from django.test import TestCase
from django.contrib.auth.models import User as AuthUser
from .models import InvalidTokenError, User, SharedSpace
# Create your tests here.
class UserTest(TestCase):
    def create_testuser(self):
        auth_user = AuthUser.objects.create_user(username="testname", password="test")
        user = User.objects.create(auth_user=auth_user)
        return user

    def test_user_creation(self):
        user = self.create_testuser()
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.__str__(), "User: testname")

class SharedSpaceTest(TestCase):
    def create_testspace(self):
        return SharedSpace.create_space("test space")
    
    def create_testuser(self):
        auth_user = AuthUser.objects.create_user(username="testname1", password="test")
        user = User.objects.create(auth_user=auth_user)
        return user
    
    def test_space_creation(self):
        space = self.create_testspace()
        self.assertTrue(space.invite_token != "")
        self.assertEqual(space.name, "test space")
        self.assertEqual(space.__str__(), "Shared Space: test space")

    def test_space_user_connection(self):
        space = self.create_testspace()
        user = self.create_testuser()

        SharedSpace.join(user, space.invite_token)

        self.assertTrue(user.spaces.contains(space))
        with self.assertRaises(InvalidTokenError):
            SharedSpace.join(user, "")
