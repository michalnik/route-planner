from pydantic import BaseModel

from .aliases import Point, Routes, GeoJson


class RouteQuestion(BaseModel):
    start: Point
    finish: Point


class RoutesAnswer(BaseModel):
    start: Point
    finish: Point
    routes: Routes


class GeoJsonQuestion(BaseModel):
    geometry: str


class GeoJsonAnswer(BaseModel):
    geojson: GeoJson


class MapFromGeoJsonQuestion(BaseModel):
    geojson: GeoJson
    title: str = "Default map title"
    route_title: str = "Default route title"
    filename: str = "default_filename.html"


class MapQuestion(BaseModel):
    start: Point
    finish: Point
    title: str = "Default map title"
    route_title: str = "Default route title"


class MapAnswer(BaseModel):
    map: str
