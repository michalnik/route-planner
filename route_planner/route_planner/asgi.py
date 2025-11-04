import os
import django
from fastapi import FastAPI

"""
ASGI config for route_planner project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_planner.settings")
django.setup()


from django.conf import settings  # noqa: E402
from api.fastapi_views import router  # noqa: E402


app = FastAPI(
    title="Route Planner Rigorously Async",
    version="v3",
    description=(
        "Route planner API to find routes from **start** to **finish**. "
        "Final map with route drawn on it is then downloadable as HTML."
    ),
)
app.include_router(router, prefix="/fastapi/v3", tags=["Routes"])


if settings.DEBUG:
    from fastapi.staticfiles import StaticFiles

    app.mount(settings.MEDIA_URL.rstrip("/"), StaticFiles(directory=settings.MEDIA_ROOT), name="media")
