from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from hub.models import Profile
from space.models import InvalidTokenError, SharedSpace

# Create your views here.

@login_required
@require_http_methods(['GET', 'POST'])
def select_space(request, space_id):
    user = Profile.objects.get(user = request.user)

    user.select_space(space_id)
    return HttpResponseRedirect("/")

@login_required
@require_http_methods(['GET', 'POST'])
def create_space(request):
    user = Profile.objects.get(user = request.user)
    space = SharedSpace.create_space("My Space", user)

    SharedSpace.join(user, space.invite_token)

    if user.selected_space is None:
        user.select_space(space.id)
    
    return HttpResponseRedirect("/")

@login_required
@require_http_methods(['POST'])
def join_space(request):
    user = Profile.objects.get(user = request.user)
    space_token = request.POST.get("space_token", None)
    if space_token is None:
        return HttpResponseRedirect("/")
    try:
        SharedSpace.join(user, space_token)
    except InvalidTokenError:
        return HttpResponseRedirect("/")

    return HttpResponseRedirect("/")

@login_required
@require_http_methods(['GET'])
def kick_from_space(request, space_id, user_id):
    user = Profile.objects.get(user = request.user)
    space = SharedSpace.objects.get(id = space_id)
    user_to_kick = Profile.objects.get(auth_user__id = user_id)
    # Only the owner can kick people
    if user == space.owner:
        if user_to_kick in space.joined_people():

            # If the owner is leaving, assign the space to the next person
            if user_to_kick == space.owner:
                try:
                    space.owner = space.joined_people()[1]
                    space.save()    
                except IndexError:
                    # Space is empty now, so remove it
                    space.delete_space()
                    return HttpResponseRedirect("/")
                
            space.leave(user_to_kick)
    return HttpResponseRedirect("/space/" + str(space_id))

@login_required
@require_http_methods(['GET', 'POST'])
def space_view(request, space_id):
    if request.method == "GET":
        user = Profile.objects.get(user = request.user)
        space = SharedSpace.objects.get(id = space_id)

        if space in user.spaces:
            user_spaces = user.spaces.all()
            selected_space = user.selected_space

            joined_people = space.joined_people()
            return render(request, "space/space-full.html", 
                          {"user": user, 
                           "space": space, 
                           "user_spaces": user_spaces, 
                           "selected_space": selected_space, 
                           'joined_people': joined_people})

        return HttpResponseRedirect("/")
    

    name = request.POST.get("name", "My Space")
    space = SharedSpace.objects.get(id = space_id)
    space.name = name
    space.save()
    return HttpResponseRedirect("/space/" + str(space_id))

@login_required
def delete_space(request, space_id):
    user = Profile.objects.get(user = request.user)
    space = SharedSpace.objects.get(id = space_id)

    if space.owner == user:
        space.delete_space()
    return HttpResponseRedirect("/")