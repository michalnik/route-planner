from typing import TypeAlias, TypedDict
from pydantic import BaseModel, Field


class Point(BaseModel):
    lat: float = Field(
        default=0.0, ge=-90, le=90, description="Latitude - angel between -90° south pole and 90° north pole."
    )
    long: float = Field(
        default=0.0,
        ge=-180,
        le=180,
        description="Longitude - angel between -180° western hemisphere" "and 180° eastern hemisphere.",
    )


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


Coordinate: TypeAlias = tuple[float, float]
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
