import typing
import functools

from .aliases import Point


class ValidationException(Exception):
    def __init__(self, code: str, message: str, data: typing.Any):
        self.code = code
        self.message = message
        self.data = data

    def __repr__(self):
        return f"Validation Error: code {self.code}, message <{self.message}>"


class ValidateRoute:

    def __call__(self, service_call: typing.Callable):
        @functools.wraps(service_call)
        def validator(instance, start: Point, finish: Point, *args, **kwargs):
            self.validate(start, finish)
            try:
                # TODO: consider if it would have worth to handle generator pattern (for i in generator: yield ...)
                #       currently, I decided handling simple return is enough for now
                return service_call(instance, start, finish, *args, **kwargs)
            except ValueError as exc:
                raise ValidationException("ors_exception", "Open route service API exception", exc.args[1])

        return validator

    def validate(self, start: Point, finish: Point):  # noqa: C901[6]
        errors: dict[str, dict[str, dict]] | dict = {}
        for name, point in [("start", start), ("finish", finish)]:
            try:
                self.validate_point(point)
            except ValueError as exc:
                errors[name] = {}
                for field_name, args in exc.args:
                    errors[name].update({field_name: {"message": args[0], "value": args[1]}})
        if errors:
            raise ValidationException("invalid_arguments", "Invalid arguments", errors)

    def validate_point(self, value: Point):
        errors: list[tuple[str, tuple[str, float, str]]] | list = []
        self.validate_lat(value["lat"], errors)
        self.validate_long(value["long"], errors)
        if errors:
            raise ValueError(*errors)

    @staticmethod
    def validate_lat(value: float, errors: list[tuple[str, tuple[str, float, str]]]):
        if value < -90 or value > 90:
            errors.append(("lat", ("Latitude is out of range.", value, "invalid")))

    @staticmethod
    def validate_long(value: float, errors: list[tuple[str, tuple[str, float, str]]]):
        if value < -180 or value > 180:
            errors.append(("long", ("Longitude is out of range.", value, "invalid")))
