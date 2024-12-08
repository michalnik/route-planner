from setuptools import find_packages, setup  # type: ignore

BASE_DEPENDENCIES = [
    "celery",
    "django==3.2.23",
    "django-filter",
    "django-stubs[compatible-mypy]",
    "djangorestframework",
    "djangorestframework-stubs[compatible-mypy]",
    "drf-spectacular",
    "python-dateutil",
    "requests",
    "folium",
    "openrouteservice",
]

DEV_DEPENDENCIES = BASE_DEPENDENCIES + [
    "autopep8",
    "faker",
    "django-extensions",
    "flake8",
    "mypy",
    "ipython",
    "isort",
    "markdown",
    "pre-commit",
    "pytest",
    "pytest-django",
    "rich"
]

PROD_DEPENDENCIES = BASE_DEPENDENCIES + [
    "gunicorn[gthread]",
]

setup(
    name="route-planner",
    version="0.1.0",
    author="Michal Mládek",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=BASE_DEPENDENCIES,
    extras_require={
        "dev": DEV_DEPENDENCIES,
        "prod": PROD_DEPENDENCIES,
    },
    python_requires=">=3.10",
)
