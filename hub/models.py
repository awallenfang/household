from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
# Create your models here.

from space.models import SharedSpace
class Profile(models.Model):
    user = models.OneToOneField(User, 
                                    verbose_name=_("Auth user"),
                                     null=False, 
                                     on_delete=models.CASCADE)
    spaces = models.ManyToManyField(SharedSpace, verbose_name=_("Spaces"))
    selected_space = models.ForeignKey(SharedSpace, 
                                        verbose_name=_("Selected Space"),
                                       on_delete=models.SET_NULL, 
                                       related_name="selected_space", 
                                       null=True, 
                                       blank=True)

    def __str__(self):
        return f'Profile: {self.user.username}'
    
    def select_space(self, space_id):
        space = get_object_or_404(SharedSpace, id=space_id)
        if self.spaces.contains(space):
            self.selected_space = space
            self.save()

