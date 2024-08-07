from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "hub"

urlpatterns = [
    # path('', include("transactions.urls")),
    # path('todos/', include("todos.urls")),
    path('', views.hub, name="hub"),
    path('login/', views.login, name="login"),
    path('signup/', views.signup, name="signup"),
    path('logout/', views.logout, name="logout"),
    path('select_space/<int:space_id>', views.select_space, name="select_space"),
    path('create_space', views.create_space, name="create_space"),

]