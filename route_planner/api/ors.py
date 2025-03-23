from openrouteservice import Client
from openrouteservice.directions import directions
from openrouteservice.convert import decode_polyline

from django.conf import settings
from .aliases import BoundingBox, Directions, GeoJson


osr_client = Client(
    key=settings.ROUTE["api_key"],
    timeout=settings.ROUTE["timeout"],
    retry_timeout=settings.ROUTE["retry_timeout"],
)


def find_routes(coordinates: BoundingBox, include_bbox: bool = False, include_metadata: bool = False) -> Directions:
    """
    It receives coordinates of start and end of a required path and returns
    the created map with desired filename in it, resp. it returns path to HTML map on the file system

    Args:
        coordinates: ((startX, startY), (endX, endY))
        include_bbox: flag -> true if bbox should be returned
        include_metadata: flag -> true if metadata should be returned

    Returns:
        list of routes (more structured)
    """
    found_routes: Directions = directions(osr_client, coordinates, profile=settings.ROUTE["profile"])
    return {
        "bbox": found_routes["bbox"] if include_bbox else None,
        "routes": found_routes["routes"],
        "metadata": found_routes["metadata"] if include_metadata else None,
    }


def extract_points(polyline: str) -> GeoJson:
    """Extract geo json structure from polyline - encoded string.

    Args:
        polyline: encoded route geometry

    Returns:
        geo json data structure
    """
    return decode_polyline(polyline, False)
