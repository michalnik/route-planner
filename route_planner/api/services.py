import typing

from rest_framework.serializers import ValidationError

from .validators import ValidateRoute as validate_route
from .aliases import Point, Route
from .adapter import find_routes as find_routes_adapter


class RoutePlannerService:
    @validate_route(ValidationError)
    def find_routes(self, start: Point, finish: Point) -> typing.Iterator[Route]:
        for route in find_routes_adapter(start, finish):
            yield route
