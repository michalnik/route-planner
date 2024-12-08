import io
import typing
from typing import Iterator

import folium
import openrouteservice as opens
from django.conf import settings
from django.core.files.storage import default_storage
from openrouteservice import convert
from rest_framework import generics, response, serializers, status


class Location(serializers.Serializer):
    lat = serializers.FloatField(help_text="Latitude - angel between -90° south pole and 90° north pole.")
    long = serializers.FloatField(help_text=(
        "Longitude - angel between -180° western hemisphere"
        "and 180° eastern hemisphere."
    ))

    def validate_lat(self, value: float) -> float:
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude is out of range.")
        return value

    def validate_long(self, value: float) -> float:
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude is out of range.")
        return value


class Route(serializers.Serializer):
    map = serializers.CharField(help_text="Path to rendered HTML map.")


class RouteSer(serializers.Serializer):
    start = Location(write_only=True, help_text="Starting point of the requested route.")
    finish = Location(write_only=True, help_text="Finishing point of the requested route.")
    route = Route(read_only=True)
    directions: typing.Callable

    def read_and_decode_geo(self, directions: dict[str, typing.Any]) -> dict[str, typing.Any]:
        geometry = directions['routes'][0]['geometry']
        return convert.decode_polyline(geometry)
    def convert_to_polyline(self, geojson: dict[str, typing.Any]) -> Iterator[tuple[float, float]]:
        for polyline in geojson["coordinates"]:
            yield polyline[1], polyline[0]

    def read_map_location(self, geojson: dict[str, typing.Any]) -> tuple[float, float]:
        half_pos = round(len(geojson["coordinates"]) / 2)
        index = half_pos - 1 if half_pos > 0 else half_pos
        location = geojson["coordinates"][index]
        return location[1], location[0]

    def prepare_coords(self, validated_data: dict[str, typing.Any]) -> tuple[tuple[float, float], tuple[float, float]]:
        return (
            (
                validated_data["start"]["long"],
                validated_data["start"]["lat"],
            ),
            (
                validated_data["finish"]["long"],
                validated_data["finish"]["lat"],
            )
        )

    def create_map(self, polylines: typing.Iterator[tuple[float, float]], location: tuple[float, float]) -> str:
        created_map = folium.Map(location=location, title="Found route")
        pl = folium.PolyLine(polylines, tooltip="Driving path").add_to(created_map)
        created_map.fit_bounds(pl.get_bounds())
        buffer = io.BytesIO()
        created_map.save(buffer, close_file=False)
        buffer.seek(0)
        return default_storage.save("found_route.html", buffer)

    def save(self, **kwargs):
        self.directions = getattr(opens.Client(key=settings.ROUTE["api_key"]), "directions")
        return super().save(**kwargs)

    def create(self, validated_data: dict[str, typing.Any]) -> dict[str, typing.Any]:
        directions = self.directions(self.prepare_coords(validated_data), profile=settings.ROUTE["profile"])
        geojson = self.read_and_decode_geo(directions)
        polylines = self.convert_to_polyline(geojson)
        file_path_map = self.create_map(polylines, self.read_map_location(geojson))
        return {"route": {"map": self.context["request"].build_absolute_uri(settings.MEDIA_URL + file_path_map)}}


class RouteFind(generics.GenericAPIView):
    """### Call parameters
    - **start** route location
    - **finish** route location (both within the **USA**)

    ### Call result
    - **a map** of the route
    - **optimal locations** to fuel up

    *optimal* mostly means cost-effective based on fuel prices

    Example:
    ```json
    {
        "start": {
            "lat": 40.658714,
            "long": -73.801984
        },
        "finish": {
            "lat": 33.948344,
            "long": -118.395067
        }
    }
    ```
    """
    serializer_class = RouteSer

    def post(self, request, api_ver=None):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return response.Response(data=ser.data, status=status.HTTP_200_OK)
