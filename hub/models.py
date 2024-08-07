import random
import string

from django.db import models
from django.contrib.auth.models import User as AuthUser
# Create your models here.

class InvalidTokenError(Exception):
    pass

class SharedSpace(models.Model):
    name = models.TextField(null=False, blank=False, default="My Shared Living Space", max_length=100)
    invite_token = models.TextField(max_length=10, null=False, blank=False)

    def __str__(self):
        return f'Shared Space: {self.name}'
    
    def create_space(name: str):
        invite_token = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))

        # Check if invite_token exists already
        spaces = SharedSpace.objects.filter(invite_token = invite_token)
        while len(spaces) > 0:
            invite_token = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
            spaces = SharedSpace.objects.filter(invite_token = invite_token)

        return SharedSpace.objects.create(name=name, invite_token=invite_token)
    
    def join(user, token):
        try:
            space_with_token = SharedSpace.objects.get(invite_token = token)
        except:
            raise InvalidTokenError("There is no space with the given token")
        else:
            user.spaces.add(space_with_token)
            user.save()


class User(models.Model):
    auth_user = models.OneToOneField(AuthUser, null=False, on_delete=models.CASCADE)
    spaces = models.ManyToManyField(SharedSpace)
    selected_space = models.ForeignKey(SharedSpace, on_delete=models.CASCADE, related_name="selected_space", null=True, blank=True)

    def __str__(self):
        return f'User: {self.auth_user.username}'
    
    def select_space(self, space_id):
        space = SharedSpace.objects.get(id=space_id)
        if self.spaces.contains(space):
            self.selected_space = space

        self.save()

