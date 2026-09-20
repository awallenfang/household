"""
URL configuration for p project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns


def healthz(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("i18n/", include("django.conf.urls.i18n"), name="set_language"),
] + i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include(("hub.urls", "hub"), namespace="hub")),
    path('todos/', include(("todos.urls", "urls"), namespace="todos")),
    path('space/', include(("space.urls", "space"), namespace="space")),
    path('budget/', include(("budget.urls", "budget"), namespace="budget")),
    path('accounts/', include("django.contrib.auth.urls"))
)

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()
