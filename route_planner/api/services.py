import typing

from ninja.errors import ValidationError

from .aliases import Point, Route, Routes, GeoJson
from .adapter import find_routes as find_routes_adapter, ORSException, extract_points


class RoutePlannerService:
    def find_routes(self, start: Point, finish: Point) -> Routes:
        try:
            return find_routes_adapter(start, finish)
        except ORSException as exc:
            error_details: list[dict[str, typing.Any]] = [
                {"msg": exc.message, "type": exc.code, "ctx": {"status": exc.status, "error": exc.data}}
            ]
            raise ValidationError(error_details)

    def extract_geojson(self, geometry: str) -> GeoJson:
        route: Route = {
            "way_points": [],
            "summary": {"distance": 0.0, "duration": 0.0},
            "segments": [],
            "bbox": [0.0, 0.0, 0.0, 0.0],
            "geometry": geometry,
        }
        geojson: GeoJson = extract_points(route)
        return geojson
