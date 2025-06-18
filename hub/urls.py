from django.urls import path

from . import views

app_name = "hub"

urlpatterns = [
    # path('', include("transactions.urls")),
    # path('todos/', include("todos.urls")),
    path('', views.hub, name="hub"),
    # path('login/', views.login, name="login"),
    path('accounts/signup/', views.signup, name="signup"),
    # path('logout/', views.logout, name="logout"),
    path('set_language/', views.set_language, name='set_language'),
]
