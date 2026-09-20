import logging
import os
import secrets

from celery import shared_task
from django.contrib.auth.models import User

from .models import SharedSpace
from todos.models import Todo
from hub.models import Profile

playground_todos = [
    {
        "name": "Clean kitchen",
        "done": True,
        "position": 0
    },
    {
        "name": "Do laundry",
        "done": False,
        "position": 0
    },
    {
        "name": "Buy groceries",
        "done": False,
        "position": 1
    },
    {
        "name": "Pay bills",
        "done": True,
        "position": 1
    },
    {
        "name": "Call mom",
        "done": True,
        "position": 2
    },
    {
        "name": "Read a book",
        "done": True,
        "position": 3
    },
    {
        "name": "World Domination",
        "done": False,
        "position": 2
    }
]

@shared_task
def reset_playground():
    logging.info("Resetting playground space")
    space = SharedSpace.objects.get(invite_token="PLAYGROUND", locked=True)
    Todo.objects.filter(space=space).delete()
    for todo in playground_todos:
        Todo.objects.create(space=space, name=todo["name"], done=todo["done"], position=todo["position"])

@shared_task
def create_playground():
    if os.environ.get("PLAYGROUND_ENABLED", "True") != "True":
        logging.info("Playground creation disabled, skipping.")
        return
    from django.conf import settings as django_settings

    if not django_settings.DEBUG:
        logging.warning("Refusing to create playground accounts with DEBUG=False.")
        return
    invite_key = "PLAYGROUND"
    locked = True
    owner = None
    name = "Playground"

    space, created = SharedSpace.objects.get_or_create(invite_token=invite_key, locked=locked, owner=owner, name=name)
    # Create playground accounts
    # Alice, Bob, Charlie
    def _ensure_playground_user(username, env_var):
        user, user_created = User.objects.get_or_create(username=username)
        if user_created:
            password = os.environ.get(env_var) or secrets.token_urlsafe(24)
            user.set_password(password)
            user.save()
        return user

    alice = _ensure_playground_user("alice", "PLAYGROUND_ALICE_PASSWORD")
    bob = _ensure_playground_user("bob", "PLAYGROUND_BOB_PASSWORD")
    charlie = _ensure_playground_user("charlie", "PLAYGROUND_CHARLIE_PASSWORD")

    alice_profile, _ = Profile.objects.get_or_create(user=alice)
    bob_profile, _ = Profile.objects.get_or_create(user=bob)
    charlie_profile, _ = Profile.objects.get_or_create(user=charlie)
    for playground_profile in (alice_profile, bob_profile, charlie_profile):
        if not playground_profile.playground_account:
            playground_profile.playground_account = True
            playground_profile.save()

    alice_profile.spaces.add(space)
    bob_profile.spaces.add(space)
    charlie_profile.spaces.add(space)

    alice_profile.selected_space = space
    bob_profile.selected_space = space
    charlie_profile.selected_space = space

    alice_profile.save()
    bob_profile.save()
    charlie_profile.save()

    if created:
        logging.info("Created playground space")
        # Set up todos
        for todo in playground_todos:
            Todo.objects.create(space=space, name=todo["name"], done=todo["done"], position=todo["position"])
    else:
        logging.info("Playground space already exists")
        # Reset todos
        for todo in Todo.objects.filter(space=space):
            todo.delete()

        for todo in playground_todos:
            Todo.objects.create(space=space, name=todo["name"], done=todo["done"], position=todo["position"])
