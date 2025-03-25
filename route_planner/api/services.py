from .validators import ValidateRoute as validate_route
from .aliases import Point, Routes
from .adapter import find_routes as find_routes_adapter


class RoutePlannerService:
    @validate_route()
    def find_routes(self, start: Point, finish: Point) -> Routes:
        return find_routes_adapter(start, finish)
