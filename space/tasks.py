import logging

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
    # Create playground if it doesn't exist
    logging.info("Resetting playground space")
        # Reset todos
    for todo in Todo.objects.filter(space=space):
        todo.delete()

    for todo in playground_todos:
        Todo.objects.create(space=space, name=todo["name"], done=todo["done"], position=todo["position"])

@shared_task
def create_playground():
    invite_key = "PLAYGROUND"
    locked = True
    owner = None
    name = "Playground"

    space, created = SharedSpace.objects.get_or_create(invite_token=invite_key, locked=locked, owner=owner, name=name)
    # Create playground accounts
    # Alice, Bob, Charlie


    alice, _ = User.objects.get_or_create(username="alice")
    alice.set_password("secure_password_1")
    alice.save()

    bob, _ = User.objects.get_or_create(username="bob")
    bob.set_password("secure_password_2")
    bob.save()

    charlie, _ = User.objects.get_or_create(username="charlie")
    charlie.set_password("secure_password_3")
    charlie.save()

    alice_profile, _ = Profile.objects.get_or_create(user=alice, playground_account=True)
    bob_profile, _ = Profile.objects.get_or_create(user=bob, playground_account=True)
    charlie_profile, _ = Profile.objects.get_or_create(user=charlie, playground_account=True)

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
