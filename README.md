# Django SensorThings

A Django extension that adds [OGC SensorThings API v1.1](https://www.ogc.org/standard/sensorthings/) support to your project. It provides a fully compliant REST API for managing sensor data, built on top of [Django Ninja](https://django-ninja.dev/) and [Pydantic](https://docs.pydantic.dev/).

## Features

- Full SensorThings API v1.1 compliance (Things, Locations, Datastreams, Observations, and more)
- Built-in Django ORM backend
- Optional extensions: Data Array, MultiDatastream
- Extensible backend adapter interface for custom storage layers

## Installation

```
pip install django-sensorthings
```

## Quick Start

**1. Add the apps to `INSTALLED_APPS`:**

```python
INSTALLED_APPS = [
    ...
    "sensorthings.versions.v1_1",
    "sensorthings.versions.v1_1.backends.django",
]
```

To enable optional extensions, add them as well:

```python
    "sensorthings.versions.v1_1.extensions.dataarray",
```

**2. Configure the library in your settings:**

```python
from uuid import UUID

SENSORTHINGS_V1_1_SERVICE_URL = "http://localhost:8000/sensorthings"
SENSORTHINGS_V1_1_BACKEND_ADAPTER = "sensorthings.versions.v1_1.backends.django.adapter.DjangoBackendAdapter"
SENSORTHINGS_V1_1_ID_TYPE = UUID
SENSORTHINGS_V1_1_ID_DELIMITER = "'"
```

**3. Include the URL patterns:**

```python
from django.urls import path, include

urlpatterns = [
    ...
    path("sensorthings/", include("sensorthings.versions.v1_1.urls")),
]
```

**4. Run migrations:**

```
python manage.py migrate
```

The API will be available at `http://localhost:8000/sensorthings/v1.1/`.

Interactive API docs (Swagger UI) are served at `http://localhost:8000/sensorthings/v1.1/docs`.

## Configuration Reference

| Setting | Description |
|---|---|
| `SENSORTHINGS_V1_1_SERVICE_URL` | Base URL of the service, used when building self links and navigation links |
| `SENSORTHINGS_V1_1_BACKEND_ADAPTER` | Dotted path to the backend adapter class |
| `SENSORTHINGS_V1_1_ID_TYPE` | Python type used for entity IDs (e.g. `UUID`, `int`) |
| `SENSORTHINGS_V1_1_ID_DELIMITER` | Delimiter wrapping IDs in URLs (e.g. `'` for `Things('id')`) |

## Extensions

### Data Array

Adds the `$resultFormat=dataArray` query parameter to the Observations endpoint, which returns observations grouped by Datastream in a compact array format.

```python
INSTALLED_APPS = [
    ...
    "sensorthings.versions.v1_1.extensions.dataarray",
]
```

### MultiDatastream

Adds support for the MultiDatastream entity type, which associates a single Datastream with multiple observed properties.

```python
INSTALLED_APPS = [
    ...
    "sensorthings.versions.v1_1.extensions.multidatastream",
]
```