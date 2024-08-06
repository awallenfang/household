from django.db import models
from django.contrib.auth.models import User as AuthUser
# Create your models here.

class SharedSpace(models.Model):
    name = models.TextField(null=False, blank=False, default="My Shared Living Space", max_length=100)
    invite_token = models.TextField(max_length=10, null=False, blank=False)

class User(models.Model):
    auth_user = models.OneToOneField(AuthUser, null=False, on_delete=models.CASCADE)
    spaces = models.ManyToManyField(SharedSpace)


