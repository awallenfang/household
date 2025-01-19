from functools import wraps
from django.core.exceptions import PermissionDenied
from hub.models import User


def space_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = User.objects.get(auth_user = request.user)
        if user.selected_space is None:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return wrap