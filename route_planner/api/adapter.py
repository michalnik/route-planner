from typing import Iterator
import folium
from dataclasses import dataclass

from django.core.files.storage import default_storage, Storage

from .aliases import Point, BoundingBox, Route, ORSPoint, GeoJson
from .ors import load_routes as ors_load_routes, extract_points as ors_extract_points


@dataclass
class File:
    url: str
    name: str
    size: int

    def __init__(self, filename: str, created_map: folium.Map, storage: Storage | None = None):
        self._storage: Storage = storage if storage is not None else default_storage
        self._map: folium.Map = created_map
        self.name = self._storage.get_available_name(filename)
        with self._storage.open(self.name, "wb") as file_handler:
            self._map.save(file_handler, close_file=False)
            self.size = file_handler.tell()
            self.url = self._storage.url(self.name)


def load_routes(start: Point, finish: Point) -> Iterator[Route]:
    """It is just adapter to prepare input parameters for ORS call from validated data

    Args:
       start: starting point route coordinates
       finish: ending point route coordinates

    Returns:
       list of routes (more structured)
    """
    coordinates: BoundingBox = (
        (
            start["long"],
            start["lat"],
        ),
        (
            finish["long"],
            finish["lat"],
        ),
    )
    for route in ors_load_routes(coordinates)["routes"]:
        yield route


def extract_points(route: Route) -> GeoJson:
    """It extracts GeoJson structure from polyline - encoded string.

    Args:
        route: found route created by ORS

    Returns:
        GeoJson structure
    """
    polyline: str = route["geometry"]
    return ors_extract_points(polyline)


def geojson_iterable(geo_json: GeoJson, reverse: bool = True) -> Iterator[ORSPoint]:
    """It is not just generator of coordinates from ORS service,
    but it can reverse lat with long also.

    Args:
        geo_json: it contains decoded polyline as list of ORS coordinates
        reverse: default true -> switch lat with long

    Returns:
        generator of ORS coordinates
    """
    if reverse:
        yield from map(
            lambda osr_point: osr_point.reverse() or osr_point, geo_json["coordinates"]  # type: ignore[func-returns-value]  # noqa: [E501]
        )
    else:
        yield from geo_json["coordinates"]


def create_map(
    start: Point, finish: Point, title: str = "Found routes", route_title: str = "Driving path"
) -> folium.Map:
    """It creates HTML map with route found from start to finish points.
     Map title and route title can be set.

    Args:
        start: start of the route
        finish: end of the route
        title: title of the map
        route_title: title of the route

    Returns:
        generated HTML map
    """
    created_map = folium.Map(title=title)
    drawn_polyline: folium.PolyLine | None = None
    gj_iterable: Iterator[ORSPoint]
    for route in load_routes(start, finish):
        geojson: GeoJson = extract_points(route)
        gj_iterable = geojson_iterable(geojson)
        drawn_polyline = folium.PolyLine(gj_iterable, tooltip=route_title)
        created_map.add_child(drawn_polyline)
    else:
        if drawn_polyline is not None:
            # center map on last polyline
            created_map.fit_bounds(drawn_polyline.get_bounds())
    return created_map
