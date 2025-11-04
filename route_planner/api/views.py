import typing
from rest_framework import mixins, viewsets
from ninja import NinjaAPI, throttling

from django.conf import settings

from .adapter import ORSException
from .ninja_schema import (
    RouteQuestion,
    RoutesAnswer,
    GeoJsonQuestion,
    GeoJsonAnswer,
    MapFromGeoJsonQuestion,
    MapQuestion,
    MapAnswer,
)
from .services import RoutePlannerService
from .serializers import RouteSer


api = NinjaAPI(
    title="Route Planner",
    version="v2",
    description=(
        "Route planner API to find routes from **start** to **finish**. "
        "Final map with route drawn on it is then downloadable as HTML."
    ),
    throttle=[
        throttling.AnonRateThrottle(settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["anon"]),
        throttling.UserRateThrottle(settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["user"]),
    ],
)


@api.post("/routes", response=RoutesAnswer, tags=["Routes"])
def find_routes(request, route: RouteQuestion):
    """### Call parameters
    - **start** route location
    - **finish** route location (both within the **USA**)

    ### Call result
    - includes start end finish points of the requested routes
    - textual representation of the all found routes

    Example:
    ```json
    {
        "start": {
            "lat": 40.658714,
            "long": -73.801984
        },
        "finish": {
            "lat": 33.948344,
            "long": -118.395067
        }
    }
    ```
    """
    from ninja.errors import ValidationError

    try:
        RoutePlannerService().find_routes(route.start, route.finish)
    except ORSException as exc:
        error_details: list[dict[str, typing.Any]] = [
            {"msg": exc.message, "type": exc.code, "ctx": {"status": exc.status, "error": exc.data}}
        ]
        raise ValidationError(error_details)
    return {
        "start": route.start,
        "finish": route.finish,
        "routes": RoutePlannerService().find_routes(route.start, route.finish),
    }


@api.post("/geojson", response=GeoJsonAnswer, tags=["Routes"])
def extract_geojson(request, route: GeoJsonQuestion):
    """### Call parameters
    - **geometry** geometry string read from route data structure returned from `/routes` endpoint.

    ### Call result
    - geojson structure
        - type = "LineString"
        - coordinates: list of Open Route Service points(coordinates)

    Example:
    ```json
    {
    "geometry": "cddwFbomaM..."
    }
    ```
    """
    return {"geojson": RoutePlannerService().extract_geojson(route.geometry)}


@api.post("/map_from_geojson", response=MapAnswer, tags=["Routes"])
def map_from_geo_json(request, query: MapFromGeoJsonQuestion):
    """### Call parameters
    - **geojson** data structure of route returned from `/geojson` endpoint.
    - **title** title of the map
    - **route_title** title of the route
    - **filename** filename of the map

    ### Call result
    - map: URL of the map
    """
    file = RoutePlannerService().map_from_geojson(
        query.geojson,
        title=query.title,
        route_title=query.route_title,
        filename=query.filename,
    )
    return {"map": request.build_absolute_uri(file.url)}


@api.post("/map", response=MapAnswer, tags=["Routes"])
def create_map(request, query: MapQuestion):
    """### Call parameters
    - **start** route location
    - **finish** route location (both within the **USA**)
    - **title** title of the map
    - **route_title** title of the route

    ### Call result
    - map: URL of the map

     Example:
    ```json
    {
        "start": {
            "lat": 40.658714,
            "long": -73.801984
        },
        "finish": {
            "lat": 33.948344,
            "long": -118.395067
        },
        "title": "Which is my way?",
        "route_title": "Route from east to west!"
    }
    ```
    """
    file = RoutePlannerService().create_map(
        query.start,
        query.finish,
        query.title,
        query.route_title,
    )
    return {"map": request.build_absolute_uri(file.url)}


class RoutesViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """### Call parameters
    - **start** route location
    - **finish** route location (both within the **USA**)

    ### Call result
    - **a map** of the route
    - **optimal locations** to fuel up

    *optimal* mostly means cost-effective based on fuel prices

    Example:
    ```json
    {
        "start": {
            "lat": 40.658714,
            "long": -73.801984
        },
        "finish": {
            "lat": 33.948344,
            "long": -118.395067
        }
    }
    ```
    """

    serializer_class = RouteSer

    def perform_create(self, ser: RouteSer):
        from rest_framework.exceptions import ValidationError

        try:
            ser.save()
        except ORSException as exc:
            error_details: list[dict[str, typing.Any]] = [
                {"msg": exc.message, "type": exc.code, "ctx": {"status": exc.status, "error": exc.data}}
            ]
            raise ValidationError(error_details)
