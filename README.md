# Django OGC SensorThings

A Django extension that adds [OGC SensorThings API v1.1](https://www.ogc.org/standard/sensorthings/) support to your project. It provides a fully compliant REST API for managing sensor data, built on top of [Django Ninja](https://django-ninja.dev/) and [Pydantic](https://docs.pydantic.dev/).

## Features

- Full SensorThings API v1.1 compliance (Things, Locations, Datastreams, Observations, and more)
- Built-in Django ORM backend
- Optional extensions: Data Array, MultiDatastream
- Extensible backend adapter interface for custom storage layers

## Installation

```
pip install django-ogc-sensorthings
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
| `SENSORTHINGS_V1_1_ID_EXAMPLE` | Example ID value shown in Swagger UI (auto-detected from `ID_TYPE` if not set) |
| `SENSORTHINGS_V1_1_MAX_TOP` | Maximum number of entities returned in a single collection response (default: `100`) |
| `SENSORTHINGS_V1_1_RENDERER` | Custom Django Ninja renderer instance (subclass of `ninja.renderers.BaseRenderer`); defaults to `JSONRenderer` |
| `SENSORTHINGS_V1_1_DOCS_ENABLED` | Whether to expose the Swagger UI and OpenAPI schema endpoints (default: `True`) |
| `SENSORTHINGS_V1_1_DEFAULT_AUTH_HANDLER` | See [Authentication and Authorization](#authentication-and-authorization) |
| `SENSORTHINGS_V1_1_AUTH_HANDLERS` | See [Authentication and Authorization](#authentication-and-authorization) |
| `SENSORTHINGS_V1_1_PROPERTIES_SCHEMAS` | See [Custom Properties Schemas](#custom-properties-schemas) |

## Authentication and Authorization

Authentication and authorization are handled at two separate layers.

### Authentication

Authentication is configured via Django settings using [Django Ninja's auth system](https://django-ninja.dev/guides/authentication/). Define one or more auth classes and assign them to the `DEFAULT_AUTH_HANDLER` setting to protect all endpoints globally:

```python
from ninja.security import HttpBearer

class BearerAuth(HttpBearer):
    def authenticate(self, request, token):
        user = validate_token(token)
        if user:
            return user

SENSORTHINGS_V1_1_DEFAULT_AUTH_HANDLER = [BearerAuth()]
```

If your auth handler is defined in a module that imports Django models, use a dotted Python path to avoid `AppRegistryNotReady` errors at settings load time:

```python
SENSORTHINGS_V1_1_DEFAULT_AUTH_HANDLER = [
    "myapp.auth.BearerAuth",
]
```

Sync auth handlers are automatically wrapped with `sync_to_async`, so they can safely perform ORM operations (session lookup, API key validation) from within async views.

To require different auth on specific operations — for example, public reads with authenticated writes — use `AUTH_HANDLERS` with the operation name as the key:

```python
SENSORTHINGS_V1_1_AUTH_HANDLERS = {
    "create_thing_entity": [BearerAuth()],
    "update_thing_entity": [BearerAuth()],
    "delete_thing_entity": [BearerAuth()],
}
```

Operation names follow the pattern `{verb}_{entity}_{collection|entity}`, for example `get_thing_collection`, `create_observation_entity`, `delete_datastream_entity`. Any operation not listed in `AUTH_HANDLERS` falls back to `DEFAULT_AUTH_HANDLER`.

### Authorization

Row-level access control — filtering results by owner, organization, or any other data-level constraint — belongs in the backend adapter via the `context` parameter, which is the Django `HttpRequest` passed to every adapter method:

```python
async def get_things(self, ..., context=None):
    return query_things(owner=context.user)
```

This keeps identity verification at the view layer and data scoping at the data layer.

## Backend Adapters

The backend adapter is the bridge between the SensorThings API layer and your data. The built-in Django ORM backend is suitable for new projects, but the main use case for this library is layering a compliant SensorThings API over an existing environmental sensor database — in which case you implement a custom adapter that maps your existing schema to the SensorThings data model.

### Implementing a Custom Adapter

Subclass the `BaseBackendAdapter` for the API version you are targeting and implement its abstract methods:

```python
from sensorthings.versions.v1_1.backends.base import BaseBackendAdapter
from sensorthings.versions.v1_1.dto import (
    EntityResultSetDTO, ThingDTO, ObservationDTO, ...
)

class MyBackendAdapter(BaseBackendAdapter):
    ...
```

Each entity type has four operations: `get_*`, `create_*`, `update_*`, and `delete_*`. You only need to implement the ones your deployment supports — raise `NotImplementedError` for any you intentionally omit. Point the `BACKEND_ADAPTER` setting to your class using a dotted path:

```python
SENSORTHINGS_V1_1_BACKEND_ADAPTER = "myapp.adapters.MyBackendAdapter"
```

### Operation Signatures

**`get_*`** — fetch a collection of entities:

```python
async def get_things(
    self,
    filters=None,       # parsed OData $filter AST node, or None
    orderby=None,       # list of OrderByField, or None
    group_by=None,      # tuple of (field_name, [ids]), or None
    select=None,        # list of field names to fetch, or None (fetch all)
    top=100,            # maximum number of results
    skip=0,             # offset
    count=False,        # whether to include total count
    context=None,       # the Django HttpRequest — use for auth, tenancy, etc.
) -> EntityResultSetDTO[ThingDTO]:
    ...
```

**`create_*`** — create one or more entities, return their IDs:

```python
async def create_things(
    self,
    payload: list[ThingDTO],
    context=None,
) -> list[app_settings.ID_TYPE]:
    ...
```

**`update_*`** — apply partial updates:

```python
async def update_things(
    self,
    payload: dict[app_settings.ID_TYPE, ThingDTO],
    context=None,
) -> None:
    ...
```

**`delete_*`** — delete by ID:

```python
async def delete_things(
    self,
    entity_ids: list[app_settings.ID_TYPE],
    context=None,
) -> None:
    ...
```

Both sync and async implementations are supported. The service layer automatically wraps synchronous methods in `sync_to_async`.

### Returning Results from `get_*`

`get_*` methods return an `EntityResultSetDTO`, which separates entity objects from collection membership to avoid duplication when grouping.

For a standard (ungrouped) query, use the `"__UNGROUPED__"` key:

```python
from sensorthings.versions.v1_1.dto import EntityResultSetDTO, CollectionDTO, ThingDTO

return EntityResultSetDTO(
    collections={
        "__UNGROUPED__": CollectionDTO(
            entity_count=total if count else None,
            entity_ids=[t.id for t in results],
        )
    },
    entities={t.id: ThingDTO(id=t.id, name=t.name, description=t.description) for t in results},
)
```

When `group_by=(field_name, ids)` is provided — used internally for `$expand` and nested resource paths — key each collection by the parent entity ID:

```python
return EntityResultSetDTO(
    collections={
        parent_id: CollectionDTO(entity_ids=[...])
        for parent_id in requested_ids
    },
    entities={obs.id: ObservationDTO(...) for obs in results},
)
```

Use `Absent` (from `sensorthings.types`) rather than `None` for DTO fields that were not requested via `$select`, so they are omitted from the response rather than serialized as null.

> **Why `Absent` and not `None`?** Python has no built-in concept of "not provided but also not null". Using `None` as a sentinel would type fields as nullable, which is incorrect — most SensorThings fields are non-nullable but conditionally omittable (e.g. omitted from a `$select` response, or not set in a PATCH body). `Absent` allows fields to carry their correct non-nullable type while still being excluded from serialization when not present.

### Transactions

Write operations (`create_entity`, `update_entity`, `delete_entity`) are automatically wrapped in a transaction using the `transaction()` context manager on your adapter. The built-in Django adapter implements this with `transaction.atomic()`, making deep inserts atomic by default.

Custom adapters inherit a no-op by default. Override `transaction()` to add transaction support for your storage layer:

```python
from contextlib import asynccontextmanager

class MyAdapter(BaseBackendAdapter):

    @asynccontextmanager
    async def transaction(self):
        async with self.session.begin():
            yield
```

For sync adapters, wrap a sync context manager inside `@asynccontextmanager`:

```python
@asynccontextmanager
async def transaction(self):
    with my_sync_transaction():
        yield
```

### Customizing Server Settings

Override `get_server_settings()` to control the conformance list advertised at the service root — for example if your adapter does not support write operations:

```python
def get_server_settings(self) -> dict:
    settings = super().get_server_settings()
    settings["conformance"] = [
        uri for uri in settings["conformance"]
        if "create-update-delete" not in uri
    ]
    return settings
```

## Custom Properties Schemas

By default, the `properties` field on each entity (and the `parameters` field on Observation) is typed as a plain `dict`. Use `SENSORTHINGS_V1_1_PROPERTIES_SCHEMAS` to replace this with a typed Pydantic model for any entity, which will be enforced on both request validation and response serialization:

```python
from pydantic import BaseModel

class ThingProperties(BaseModel):
    deployment_id: str
    site_code: str
    active: bool = True

SENSORTHINGS_V1_1_PROPERTIES_SCHEMAS = {
    "Things": ThingProperties,
}
```

The valid keys, one per entity type, are:

| Key | Entity |
|---|---|
| `"Things"` | Thing |
| `"Locations"` | Location |
| `"Datastreams"` | Datastream |
| `"Sensors"` | Sensor |
| `"ObservedProperties"` | ObservedProperty |
| `"Observations"` | Observation (`parameters` field) |
| `"FeaturesOfInterest"` | FeatureOfInterest |
| `"MultiDatastreams"` | MultiDatastream (requires MultiDatastream extension) |

Any entity not listed in the dict keeps its default `dict` type.

> **Note:** `PROPERTIES_SCHEMAS` values are compiled into the API schemas at app load time and cannot be changed at runtime. If the schema class is defined in a module that imports Django models, use a dotted Python path to defer the import until after app startup:
> ```python
> SENSORTHINGS_V1_1_PROPERTIES_SCHEMAS = {
>     "Things": "myapp.schemas.ThingProperties",
> }
> ```

## Customizing Field Types

### Observation Result Type

By default, the `result` field on Observation is typed as `float`. Use `OBSERVATION_TYPE_SCHEMA` to change the accepted Python type:

```python
from typing import Union

SENSORTHINGS_V1_1_OBSERVATION_TYPE_SCHEMA = Union[float, str, bool]
```

Use `OBSERVATION_TYPE_VALUE_LITERAL` to restrict the set of allowed `observationType` URIs on Datastream:

```python
from typing import Literal

SENSORTHINGS_V1_1_OBSERVATION_TYPE_VALUE_LITERAL = Literal[
    "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
]
```

### Encoding Types

Three entity types carry an `encodingType` field alongside an associated data field (`location`, `metadata`, or `feature`). Each has a pair of settings: one for the Python type of the data field and one for the allowed `encodingType` values.

| Setting | Affects | Default |
|---|---|---|
| `SENSORTHINGS_V1_1_LOCATION_ENCODING_TYPE_SCHEMA` | Location `location` field type | `dict` |
| `SENSORTHINGS_V1_1_LOCATION_ENCODING_TYPE_VALUE_LITERAL` | Allowed Location `encodingType` values | `"application/geo+json"` |
| `SENSORTHINGS_V1_1_SENSOR_METADATA_ENCODING_TYPE_SCHEMA` | Sensor `metadata` field type | `str` |
| `SENSORTHINGS_V1_1_SENSOR_METADATA_ENCODING_TYPE_VALUE_LITERAL` | Allowed Sensor `encodingType` values | `"application/pdf"`, SensorML 2.0, `"text/html"` |
| `SENSORTHINGS_V1_1_FEATURE_OF_INTEREST_ENCODING_TYPE_SCHEMA` | FeatureOfInterest `feature` field type | `dict` |
| `SENSORTHINGS_V1_1_FEATURE_OF_INTEREST_ENCODING_TYPE_VALUE_LITERAL` | Allowed FeatureOfInterest `encodingType` values | `"application/geo+json"` |

Example — enforce a typed GeoJSON structure on FeatureOfInterest:

```python
from typing import Literal
from pydantic import BaseModel

class GeoJSONFeature(BaseModel):
    type: str
    geometry: dict
    properties: dict

SENSORTHINGS_V1_1_FEATURE_OF_INTEREST_ENCODING_TYPE_SCHEMA = GeoJSONFeature
SENSORTHINGS_V1_1_FEATURE_OF_INTEREST_ENCODING_TYPE_VALUE_LITERAL = Literal["application/geo+json"]
```

> **Note:** Like `PROPERTIES_SCHEMAS`, these values cannot be changed at runtime. Dotted Python paths are supported for any of these settings when the referenced type is defined in a module that imports Django models.

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
