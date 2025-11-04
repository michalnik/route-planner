from django.urls import path, include
from rest_framework.routers import DefaultRouter, APIRootView, Route
from .views import RoutesViewSet


class RouteRootView(APIRootView):
    """
    To find routes from **start** to **finish**.
    Final map with route drawn on it is then downloadable as `HTML`.
    """

    def get_view_name(self):
        return "Route Planner API"


class RouteRouter(DefaultRouter):
    APIRootView = RouteRootView
    routes = [
        Route(
            url=r"^{prefix}{trailing_slash}$",
            mapping={"post": "create"},
            name="{basename}-create",
            detail=False,
            initkwargs={"suffix": "Create"},
        ),
    ]


drf_router = RouteRouter()
drf_router.register("routes", RoutesViewSet, basename="routes")


urlpatterns = [
    path("", include(drf_router.urls)),
]
