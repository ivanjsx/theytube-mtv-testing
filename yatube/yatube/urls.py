"""
yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path("", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path("", Home.as_view(), name="home")
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path("blog/", include("blog.urls"))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(route="", view=include(arg="posts.urls", namespace="posts")),
    path(route="auth/", view=include(arg="users.urls", namespace="users")),
    path(route="auth/", view=include(arg="django.contrib.auth.urls")),
    path(route="about/", view=include(arg="about.urls", namespace="about")),
    path(route="admin/", view=admin.site.urls, name="admin"),
]

handler304 = "core.views.not_modified_304"

handler400 = "core.views.bad_request_400"
handler403 = "core.views.forbidden_403"
handler404 = "core.views.not_found_404"

handler500 = "core.views.internal_server_error_500"

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
