import random
import string

from django.db import models



# Create your models here.

class InvalidTokenError(Exception):
    pass

class SharedSpace(models.Model):
    name = models.TextField(null=False, blank=False, default="My Shared Living Space", max_length=100)
    invite_token = models.TextField(max_length=10, null=False, blank=False)
    owner = models.ForeignKey('hub.User', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Shared Space: {self.name}'
    
    @staticmethod
    def create_space(name: str, owner):
        invite_token = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))

        # Check if invite_token exists already
        spaces = SharedSpace.objects.filter(invite_token = invite_token)
        while len(spaces) > 0:
            invite_token = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
            spaces = SharedSpace.objects.filter(invite_token = invite_token)
    

        return SharedSpace.objects.create(name=name, invite_token=invite_token, owner=owner)
    
    @staticmethod
    def join(user, token):
        try:
            space_with_token = SharedSpace.objects.get(invite_token = token)
        except SharedSpace.DoesNotExist as exc:
            raise InvalidTokenError("There is no space with the given token") from exc
        user.spaces.add(space_with_token)
        user.save()

    def leave(self, user):
        user.spaces.remove(self)
        if user == self.owner:
            try:
                self.owner = self.joined_people()[0]
                self.save()
            except IndexError:
                # Space is empty now, so remove it
                self.delete_space()
        user.save()

    def joined_people(self):
        # Avoid a circular import with this
        from hub.models import User

        users = User.objects.filter(spaces__in=[self])
        return list(users)
    
    def delete_space(self):
        self.delete()
