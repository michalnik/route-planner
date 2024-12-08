from django.urls import path

from .views import RouteFind

urlpatterns = [
    path("", RouteFind.as_view(), name="route-find"),
]
