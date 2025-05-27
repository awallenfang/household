from todos.models import Todo
from hub.models import Profile

def delete_todo(request, todo_id, *args, **kwargs):
    """
    Deletes a todo item.
    """

    todo = Todo.objects.get(id=todo_id)

    if todo.space == Profile.objects.get(user = request.user).selected_space:
        todo.delete()

        return True
    return False

def create_todo(request, *args, **kwargs):
    """
    Add a new todo with default values
    """
    user  = Profile.objects.get(user = request.user)
    try:
        todo = Todo.create_in_space(user.selected_space)

        todo.assign_user(user)

        return True
    except:
        return False