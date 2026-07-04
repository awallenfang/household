from django.shortcuts import redirect
from django.views.generic import ListView, View, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator


from hub.decorators import space_required
from hub.mixins import HTMXMixin
from hub.models import Profile
from todos.forms import TodoForm
from todos.renderers import *
from todos.actions import *

from .models import Todo

@method_decorator(login_required, name='dispatch')
@method_decorator(space_required, name='dispatch')
class TodoDashboard(HTMXMixin, ListView):
    model = Todo
    template_name = "todos/dashboard_full.html"
    context_object_name = "todos"
    partials = {
        "todo_list": render_todo_list,
        "reorder_list": (render_todo_list, reorder_list)
    }
    
    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        return Todo.objects.filter(space=profile.selected_space).order_by('position', 'done')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todos = Todo.get_open(self.request)

        finished_todos = Todo.get_closed(self.request)

        user = Profile.objects.get(user = self.request.user)
        user_spaces = user.get_spaces
        selected_space = user.selected_space
        context.update({
            'todos': todos,
            'finished_todos': finished_todos,
            'user_spaces': user_spaces,
            'selected_space': selected_space
        })
        return context
    
    def delete(self, request, **kwargs):
        """
        Handle the deletion of a todo item.
        """
        todo_id = kwargs.get('pk')
        todo = get_object_or_404(Todo, id=todo_id)
        
        if todo.space == Profile.objects.get(user=request.user).selected_space:
            todo.delete()
        
        return render_todo_list(request)

@method_decorator(login_required, name='dispatch')
@method_decorator(space_required, name='dispatch')
class DeleteTodoView(HTMXMixin, View):
    partials = {
        "todo_list": (render_todo_list, delete_todo)
    }

    def delete(self, request, todo_id):
        delete_todo(request, todo_id)

@method_decorator(login_required, name='dispatch')
@method_decorator(space_required, name='dispatch')
class CreateTodoView(HTMXMixin, View):
    model = Todo
    partials = {
        "create_todo": (render_todo_list, create_todo)
    }

    def get(self, request, *args, **kwargs):
        create_todo(request, *args, **kwargs)
        return redirect("todos:todos")
    
    def post(self, request, *args, **kwargs):
        create_todo(request, *args, **kwargs)
        return redirect("todos:todos")

@method_decorator(login_required, name='dispatch')
@method_decorator(space_required, name='dispatch')
class TodoDetailView(HTMXMixin, View):
    partials = {
        "add_schedule": (render_todo, add_schedule),
        "open_todo": (render_todo_list, open_todo),
        "close_todo": (render_todo_list, close_todo)
    }

@method_decorator(login_required, name='dispatch')
@method_decorator(space_required, name='dispatch')
class EditTodoView(UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = "todos/components/todo_edit.html"
    pk_url_kwarg = "todo_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user = self.request.user)

        context["form"] = self.form_class(space=profile.selected_space, instance=self.get_object())
        context["todo"] = self.get_object()
        return context
    
    def form_valid(self, form):
        if form.is_valid():
            form.save()
        return render_todo(self.request, self.get_object().id)

@method_decorator(login_required, name='dispatch')
@method_decorator(space_required, name='dispatch')
class ScheduleDetailView(HTMXMixin, View):
    partials = {
        "remove_schedule": (render_todo_list, remove_schedule),
        "add_users": (render_schedule_editor, add_users),
        "change_rate": (render_schedule_editor, rate_change),
        "delete_position": (render_schedule_editor, delete_position),
        "reorder_user": (render_schedule_editor, reorder_user),
        "set_position": (render_schedule_editor, set_position)
    }

    def get(self, request, todo_id, *args, **kwargs):
        return render_schedule_editor(request, todo_id)

