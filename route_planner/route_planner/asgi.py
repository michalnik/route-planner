import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI

"""
ASGI config for route_planner project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_planner.settings")
django.setup()


from django.conf import settings  # noqa: E402
from api.fastapi_views import router  # noqa: E402


limiter = Limiter(key_func=get_remote_address, default_limits=settings.FASTAPI_THROTTLING)


app = FastAPI(
    title="Route Planner Rigorously Async",
    version="v3",
    description=(
        "Route planner API to find routes from **start** to **finish**. "
        "Final map with route drawn on it is then downloadable as HTML."
    ),
    docs_url="/fastapi/v3/docs",
    openapi_url="/fastapi/v3/openapi.json",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(router, prefix="/fastapi/v3", tags=["Routes"])


if settings.DEBUG:
    from fastapi.staticfiles import StaticFiles

    app.mount(settings.MEDIA_URL.rstrip("/"), StaticFiles(directory=settings.MEDIA_ROOT), name="media")
