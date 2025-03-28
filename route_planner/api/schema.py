from ninja import Schema

from .aliases import Point, Routes, GeoJson


class RouteQuestion(Schema):
    start: Point
    finish: Point


class RoutesAnswer(Schema):
    start: Point
    finish: Point
    routes: Routes


class GeoJsonQuestion(Schema):
    geometry: str


class GeoJsonAnswer(Schema):
    geojson: GeoJson


class MapFromGeoJsonQuestion(Schema):
    geojson: GeoJson
    title: str = "Default map title"
    route_title: str = "Default route title"
    filename: str = "default_filename.html"


class MapQuestion(Schema):
    start: Point
    finish: Point
    title: str = "Default map title"
    route_title: str = "Default route title"


class MapAnswer(Schema):
    map: str
