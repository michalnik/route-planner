"""route_planner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.reverse import reverse_lazy

from api.views import api


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy("main:route-find", kwargs={"api_ver": settings.REST_FRAMEWORK["DEFAULT_VERSION"]}),
            permanent=True,
        ),
    ),
    path("api/<str:api_ver>/", include(("api.urls", "main"))),
    path(f"ninja/{api.version}/", api.urls),
    path("admin/", admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
