import typing
import os
import django
from fastapi import FastAPI, Request

"""
ASGI config for route_planner project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_planner.settings")
django.setup()


from django.conf import settings  # noqa: E402
from api.adapter import ORSException  # noqa: E402
from api.services import RoutePlannerService  # noqa: E402
from api.fastapi_schema import (  # noqa: E402
    RouteQuestion,
    RoutesAnswer,
    GeoJsonAnswer,
    GeoJsonQuestion,
    MapFromGeoJsonQuestion,
    MapAnswer,
)


app = FastAPI()


if settings.DEBUG:
    from fastapi.staticfiles import StaticFiles

    app.mount(settings.MEDIA_URL.rstrip("/"), StaticFiles(directory=settings.MEDIA_ROOT), name="media")


api = FastAPI(
    title="Route Planner Rigorously Async",
    version="v3",
    description=(
        "Route planner API to find routes from **start** to **finish**. "
        "Final map with route drawn on it is then downloadable as HTML."
    ),
)
app.mount("/fastapi/v3", api, name="fastapi")


@api.post("/routes", response_model=RoutesAnswer, tags=["Routes"])
async def find_routes(route: RouteQuestion):
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
    from fastapi.exceptions import HTTPException

    try:
        RoutePlannerService().find_routes(route.start, route.finish)
    except ORSException as exc:
        error_details: list[dict[str, typing.Any]] = [{"msg": exc.message, "type": exc.code, "error": exc.data}]
        raise HTTPException(status_code=exc.status, detail=error_details)
    return {
        "start": route.start,
        "finish": route.finish,
        "routes": RoutePlannerService().find_routes(route.start, route.finish),
    }


@api.post("/geojson", response_model=GeoJsonAnswer, tags=["Routes"])
def extract_geojson(route: GeoJsonQuestion):
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


def build_absolute_url(request: Request, media_filepath: str) -> str:
    return f"{request.url.scheme}://{request.url.netloc}{media_filepath}"


@api.post("/map_from_geojson", response_model=MapAnswer, tags=["Routes"])
def map_from_geo_json(request: Request, query: MapFromGeoJsonQuestion):
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
    return {"map": build_absolute_url(request, file.url)}
