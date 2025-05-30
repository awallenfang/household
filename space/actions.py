import random
import string

from space.models import SharedSpace
from hub.models import Profile
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from hub.decorators import space_required

@login_required
@space_required
def kick_person(request, space_id, *args, **kwargs):
    user = Profile.objects.get(user = request.user)
    space = get_object_or_404(SharedSpace, id = space_id)
    
    # Only the owner can kick people
    if user == space.owner:
        user_id = int(request.GET.get("person_id", "-1"))
        user_to_kick = get_object_or_404(Profile, id = user_id)
        if user_to_kick in space.joined_people():

            # If the owner is leaving, assign the space to the next person
            if user_to_kick == space.owner:
                try:
                    space.owner = space.joined_people()[1]
                    space.save()    
                except IndexError:
                    # Space is empty now, so remove it
                    space.delete_space()
            space.leave(user_to_kick)
        else:
            return False    
    return  True

def regen_token(request, space_id, *args, **kwargs):
    user = Profile.objects.get(user=request.user)
    space = get_object_or_404(SharedSpace, id = space_id)

    if user.spaces.contains(space) and user == space.owner:
        invite_token = ''.join(random.choice(string.ascii_uppercase + string.digits[1:]) for _ in range(10))

        # Check if invite_token exists already
        spaces = SharedSpace.objects.filter(invite_token = invite_token)
        while len(spaces) > 0:
            invite_token = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
            spaces = SharedSpace.objects.filter(invite_token = invite_token)
        space.invite_token = invite_token
        space.save()
        return True
    return False