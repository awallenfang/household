from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from todos.models import Todo
from hub.models import Profile
from hub.decorators import space_required

@login_required
@space_required
def reorder_list(request, *args, **kwargs):
    """
    Allows the reordering on the dashboard. This will be called once a todo is dropped on a droppable space.
    It will return the id of the dropped todo, as well as the position values on the left and the right of the space.
    If it is on the edges either left or right will be set to -1, since there is no space there.
    """
    # Move position
    todo_id = int(request.GET.get("todo_id", "-1"))
    if todo_id == -1:
        return False
    changed_todo = Todo.objects.get(id=todo_id)

    if changed_todo.space == Profile.objects.get(user = request.user).selected_space:
        left = int(request.GET.get("left", "-1"))
        right = int(request.GET.get("right", "-1"))
        if left == -1 and right == -1:
            return False
        changed_todo.reorder(left, right)

        status = request.GET.get("status", "done")

        changed_todo.done =  not (status == "open") 

        changed_todo.save()
        return True

    return False

@login_required
@space_required
def delete_todo(request, todo_id, *args, **kwargs):
    """
    Deletes a todo item.
    """

    todo = Todo.objects.get(id=todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        todo.delete()

        return True
    return False

@login_required
@space_required
def create_todo(request, *args, **kwargs):
    """
    Add a new todo with default values
    """
    user  = Profile.objects.get(user = request.user)
    try:
        todo = Todo.create_in_space(user.selected_space)

        todo.assign_user(user)

        return True
    except Exception:
        return False

@login_required
@space_required
def add_schedule(request, *args, **kwargs):
    todo = Todo.objects.get(id = kwargs["todo_id"])
    if todo.space == Profile.objects.get(user = request.user).selected_space:

        user = Profile.objects.get(user = request.user)
        todo.make_scheduled([user])
        return True
    return False

@login_required
@space_required
def remove_schedule(request, *args, **kwargs):
    todo = Todo.objects.get(id = kwargs["todo_id"])
    if todo.space == Profile.objects.get(user = request.user).selected_space:
        user = Profile.objects.get(user = request.user)

        todo.schedule_state = None
        todo.save()

        todo.assign_user(user)
        return True
    return False

@login_required
@space_required
def add_users(request, *args, **kwargs):
    # TODO: Figure out why the parameter isn't caught
    users = request.GET.get("users", "").split(",")
    todo_id = kwargs["todo_id"]
    todo = Todo.objects.get(id = todo_id)
    if todo.space == Profile.objects.get(user = request.user).selected_space:
        if len(users) > 0:
            ids = [int(u) for u in users]
            todo = Todo.objects.get(id = todo_id)
            if todo.schedule_state:
                for user_id in ids:
                    if user_id == -1:
                        todo.schedule_state.add_empty()
                    else:
                        user = get_object_or_404(Profile, id = user_id)
                        todo.schedule_state.add_user(user)
        return True
    return False

@login_required
@space_required
def open_todo(request, *args, **kwargs):
    todo = Todo.objects.get(id = kwargs["todo_id"])
    if todo.space == Profile.objects.get(user = request.user).selected_space:
        todo.done = False
        todo.save()
        return True
    return False

@login_required
@space_required
def close_todo(request, *args, **kwargs):
    todo = Todo.objects.get(id = kwargs["todo_id"])
    if todo.space == Profile.objects.get(user = request.user).selected_space:
        todo.done = True
        todo.save()
        return True
    return False

@login_required
@space_required
def rate_change(request, todo_id, *args, **kwargs):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        if todo.schedule_state is None:
            return False
        rate = request.GET.get("rate", "7")
        rate = int(rate)
        todo.schedule_state.day_rotation = rate
        todo.schedule_state.save()
        return True
    return False

@login_required
@space_required
def delete_position(request, todo_id, *args, **kwargs):
    todo = Todo.objects.get(id = todo_id)
    if todo.space == Profile.objects.get(user = request.user).selected_space:
        # If it isn't scheduled do nothing
        position = request.GET.get("position", "-1")
        position = int(position)
        print(position)
        if todo.schedule_state is None or position < 0:
            return False
        todo.schedule_state.remove_user_at_position(position)
        return True
    return False

@login_required
@space_required
def reorder_user(request, todo_id, *args, **kwargs):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:

        if todo.schedule_state is None:
            return render_schedule_editor(request, todo_id)
        
        prev_pos = request.GET.get("prev_pos", "-1")
        pos = request.GET.get("pos", "-1")
        if prev_pos == "-1" and pos == "-1":
            return False
        todo.schedule_state.reorder_user(int(prev_pos), int(pos))

        return True
    return False


@login_required
@space_required
def set_position(request, todo_id, *args, **kwargs):
    todo = Todo.objects.get(id = todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        schedule = todo.schedule_state
        position = int(request.GET.get("position", "-2"))
        if schedule is None or position == -2:
            return False
        user_count = schedule.ordereduser_set.count()
        if position > user_count:
            schedule.schedule_turn = user_count - 1
        else:
            schedule.schedule_turn = position
        schedule.save()
    
        return True
    return False