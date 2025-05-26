from functools import wraps
from django.core.exceptions import PermissionDenied
from hub.models import Profile


def space_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = Profile.objects.get(user = request.user)
        if user.selected_space is None:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return wrap