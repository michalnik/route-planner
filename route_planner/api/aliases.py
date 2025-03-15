from typing import TypeAlias, TypedDict


class Point(TypedDict):
    lat: float | None
    long: float | None


class RouteSummary(TypedDict):
    distance: float
    duration: float


class WayPoints(TypedDict):
    way_points: list[int]


class Step(RouteSummary, WayPoints):
    type: int
    instruction: str
    name: str


class Segment(RouteSummary):
    steps: list[Step]


Coordinate: TypeAlias = tuple[float | None, float | None]
BoundingBox: TypeAlias = tuple[Coordinate, Coordinate]
ORSBoundingBox: TypeAlias = list[float]


class Route(WayPoints, TypedDict):
    summary: RouteSummary
    segments: list[Segment]
    bbox: ORSBoundingBox
    geometry: str


Routes: TypeAlias = list[Route]


class Directions(TypedDict):
    bbox: None
    routes: Routes
    metadata: None


ORSPoint: TypeAlias = list[float]


class GeoJson(TypedDict):
    type: str  # "LineString"
    coordinates: list[ORSPoint]
