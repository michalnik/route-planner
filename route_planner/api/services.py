import typing
import uuid

from ninja.errors import ValidationError

from .aliases import Point, Route, Routes, GeoJson
from .adapter import (
    find_routes as find_routes_adapter,
    ORSException,
    extract_points,
    create_map_from_geojson,
    File,
    create_map,
)


class RoutePlannerService:
    @staticmethod
    def find_routes(start: Point, finish: Point) -> Routes:
        try:
            return find_routes_adapter(start, finish)
        except ORSException as exc:
            error_details: list[dict[str, typing.Any]] = [
                {"msg": exc.message, "type": exc.code, "ctx": {"status": exc.status, "error": exc.data}}
            ]
            raise ValidationError(error_details)

    @staticmethod
    def extract_geojson(geometry: str) -> GeoJson:
        route: Route = {
            "way_points": [],
            "summary": {"distance": 0.0, "duration": 0.0},
            "segments": [],
            "bbox": [0.0, 0.0, 0.0, 0.0],
            "geometry": geometry,
        }
        geojson: GeoJson = extract_points(route)
        return geojson

    @staticmethod
    def map_from_geojson(
        geojson: GeoJson,
        title: str = "Default map title",
        route_title: str = "Default route title",
        filename: str = "default_file_name.html",
    ) -> File:
        created_map = create_map_from_geojson(geojson, title, route_title)
        return File(filename, created_map)

    @staticmethod
    def create_map(start: Point, finish: Point, title: str = "Found routes", route_title: str = "Driving path") -> File:
        created_map = create_map(start, finish, title, route_title)
        return File(f"{uuid.uuid4()}.html", created_map)
