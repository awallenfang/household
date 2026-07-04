from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from hub.decorators import space_required
from hub.models import Profile
from space.models import SharedSpace

def empty(_request):
    return HttpResponse("")

@login_required
@space_required
def render_space_settings(request, space_id, *args, **kwargs):
    user = Profile.objects.get(user=request.user)
    space = get_object_or_404(SharedSpace, id = space_id)

    if user.spaces.contains(space):
        selected_space = user.selected_space
        joined_people = space.joined_people()
        context = {
            "user": user,
            "space": space,
            "selected_space": selected_space,
            "joined_people": joined_people
        }
        return render(request, "space/space.html", context)
    return empty(request)

@login_required
@space_required
def render_people_list(request, space_id, *args, **kwargs):
    user = Profile.objects.get(user=request.user)
    space = get_object_or_404(SharedSpace, id = space_id)

    if user.spaces.contains(space):
        selected_space = user.selected_space
        joined_people = space.joined_people()
        context = {
            "user": user,
            "space": space,
            "selected_space": selected_space,
            "joined_people": joined_people
        }
        return render(request, "space/components/people_list.html", context)
    return empty(request)

@login_required
@space_required
def render_token(request, space_id, *args, **kwargs):
    user = Profile.objects.get(user=request.user)
    space = get_object_or_404(SharedSpace, id = space_id)

    if user.spaces.contains(space):
        return HttpResponse(str(space.invite_token))
    return empty(request)