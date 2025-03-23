from rest_framework import generics, response, status, exceptions
from ninja import Schema, NinjaAPI

from .aliases import Point, Routes
from .services import RoutePlannerService
from .serializers import RouteSer


api = NinjaAPI(
    title="Route Planner",
    version="v2",
    description=(
        "Route planner API to find routes from **start** to **finish**. "
        "Final map with route drawn on it is then downloadable as HTML."
    ),
)


@api.exception_handler(exceptions.ValidationError)
def validation_errors(request, exception):
    return api.create_response(request, exception.detail, status=status.HTTP_400_BAD_REQUEST)


class RouteQuestion(Schema):
    start: Point
    finish: Point


class RoutesAnswer(Schema):
    start: Point
    finish: Point
    routes: Routes


@api.post("/", response=RoutesAnswer, tags=["Routes"])
def get_routes(request, route: RouteQuestion):
    route_service = RoutePlannerService()
    route_service.find_routes(route.start, route.finish)
    return {
        "start": route.start,
        "finish": route.finish,
        "routes": route_service.find_routes(route.start, route.finish),
    }


class RouteFind(generics.GenericAPIView):
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

    def post(self, request, api_ver=None):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return response.Response(data=ser.data, status=status.HTTP_201_CREATED)
