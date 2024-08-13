from django.db import models
from django.contrib.auth.models import User as AuthUser
# Create your models here.

from space.models import SharedSpace

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

