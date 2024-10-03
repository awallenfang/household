from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from hub.models import User
from space.models import InvalidTokenError, SharedSpace

# Create your views here.

@login_required
@require_http_methods(['GET', 'POST'])
def select_space(request, space_id):
    user = User.objects.get(auth_user = request.user)

    user.select_space(space_id)
    return HttpResponseRedirect("/")

@login_required
@require_http_methods(['GET', 'POST'])
def create_space(request):
    user = User.objects.get(auth_user = request.user)
    space = SharedSpace.create_space("My Space", user)

    SharedSpace.join(user, space.invite_token)

    if user.selected_space is None:
        user.select_space(space.id)
        return HttpResponseRedirect("/")
    
    return HttpResponseRedirect("/")

@login_required
@require_http_methods(['POST'])
def join_space(request):
    user = User.objects.get(auth_user = request.user)
    space_id = request.POST.get("space_token", None)
    if space_id is None:
        return HttpResponseRedirect("/")
    try:
        SharedSpace.join(user, space_id)
    except InvalidTokenError:
        return HttpResponseRedirect("/")

    return HttpResponseRedirect("/")

@login_required
@require_http_methods(['GET'])
def kick_from_space(request, space_id, username):
    user = User.objects.get(auth_user = request.user)
    space = SharedSpace.objects.get(id = space_id)
    user_to_kick = User.objects.get(auth_user__username = username)
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
        user = User.objects.get(auth_user = request.user)
        space = SharedSpace.objects.get(id = space_id)

        # This isn't particularly pretty. I should solve this using a single page method with htmx soon
        user_spaces = user.spaces.all()
        selected_space = user.selected_space

        joined_people = space.joined_people()

        if user.spaces.contains(space):
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
    user = User.objects.get(auth_user = request.user)
    space = SharedSpace.objects.get(id = space_id)

    if space.owner == user:
        space.delete_space()
    return HttpResponseRedirect("/")