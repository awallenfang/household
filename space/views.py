from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from hub.models import User
from space.models import SharedSpace

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
    space = SharedSpace.create_space("My Space")
    user = User.objects.get(auth_user = request.user)
    SharedSpace.join(user, space.invite_token)

    if user.selected_space == None:
        user.select_space(space.id)
        return HttpResponseRedirect("/")
    
    return HttpResponseRedirect("/")

@login_required
@require_http_methods(['POST'])
def join_space(request):
    user = User.objects.get(auth_user = request.user)
    space_id = request.POST.get("space_token", None)
    if space_id == None:
        return HttpResponseRedirect("/")
    try:
        SharedSpace.join(user, space_id)
    except:
        return HttpResponseRedirect("/")

    return HttpResponseRedirect("/")

@login_required
@require_http_methods(['GET', 'POST'])
def space_view(request, space_id):
    if request.method == "GET":
        user = User.objects.get(auth_user = request.user)
        space = SharedSpace.objects.get(id = space_id)

        # This isn't particularly pretty. I should solve this using a single page method with htmx soon
        user_spaces = user.spaces.all()
        selected_space = user.selected_space

        if user.spaces.contains(space):
            return render(request, "space/space-full.html", {"user": user, "space": space, "user_spaces": user_spaces, "selected_space": selected_space})

        return HttpResponseRedirect("/")
    else:
        name = request.POST.get("name", "My Space")
        space = SharedSpace.objects.get(id = space_id)
        space.name = name
        space.save()
        return HttpResponseRedirect("/space/" + str(space_id))
