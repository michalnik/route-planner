import typing
import folium

from rest_framework import serializers

from .adapter import create_map, File


class Location(serializers.Serializer):
    lat = serializers.FloatField(help_text="Latitude - angel between -90° south pole and 90° north pole.")
    long = serializers.FloatField(
        help_text=("Longitude - angel between -180° western hemisphere" "and 180° eastern hemisphere.")
    )

    def validate_lat(self, value: float) -> float:
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude is out of range.")
        return value

    def validate_long(self, value: float) -> float:
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude is out of range.")
        return value


class Route(serializers.Serializer):
    map = serializers.FileField(help_text="URL of rendered HTML map.")


class RouteSer(serializers.Serializer):
    start = Location(write_only=True, help_text="Starting point of the requested route.")
    finish = Location(write_only=True, help_text="Finishing point of the requested route.")
    route = Route(read_only=True)

    def create(self, validated_data: dict[str, typing.Any]) -> dict[str, typing.Any]:
        created_map: folium.Map = create_map(validated_data["start"], validated_data["finish"])
        return {"route": {"map": File("found_route.html", created_map)}}
