from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView
from hub.models import Profile
from space.models import InvalidTokenError, SharedSpace

# Create your views here.
@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['GET']), name='dispatch')
class SpaceSettingsView(DetailView):
    model = SharedSpace
    template_name = "space/space-full.html"
    context_object_name = "space"
    pk_url_kwarg = "space_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = Profile.objects.get(user=self.request.user)
        space = self.get_object()

        if user.spaces.contains(space):
            user_spaces = user.spaces.all()
            selected_space = user.selected_space

            joined_people = space.joined_people()
            context.update({
                "user": user,
                "space": space,
                "user_spaces": user_spaces,
                "selected_space": selected_space,
                "joined_people": joined_people
            })
        else:
            return HttpResponseRedirect("/")

        return context

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
    space = get_object_or_404(SharedSpace, id = space_id)
    
    # Only the owner can kick people
    if user == space.owner:
        user_to_kick = get_object_or_404(Profile, user__id = user_id)
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
def delete_space(request, space_id):
    user = Profile.objects.get(user = request.user)
    space = get_object_or_404(SharedSpace, id = space_id)

    if space.owner == user:
        space.delete_space()
    return HttpResponseRedirect("/")