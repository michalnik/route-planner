import typing

from ninja.errors import ValidationError

from .aliases import Point, Routes
from .adapter import find_routes as find_routes_adapter, ORSException


class RoutePlannerService:
    def find_routes(self, start: Point, finish: Point) -> Routes:
        try:
            return find_routes_adapter(start, finish)
        except ORSException as exc:
            error_details: list[dict[str, typing.Any]] = [
                {"msg": exc.message, "type": exc.code, "ctx": {"status": exc.status, "error": exc.data}}
            ]
            raise ValidationError(error_details)
