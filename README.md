# HydroServer SensorThings

The HydroServer SensorThings Python package is an extension that helps implement the OGC SensorThings API specification in Django. The package is primarily built on top of the  [Django Ninja REST Framework](https://github.com/vitalik/django-ninja).

## Installation

You can install HydroServer SensorThings using pip:

```
pip install hydroserver-sensorthings
```

## Usage

To use HydroServer SensorThings in your Django project, add the following line to your `MIDDLEWARE` setting:

```
MIDDLEWARE = [
	# ...
	'sensorthings.middleware.SensorThingsMiddleware',
	# ...
]
```

To initialize the SensorThings API in your project, you must create an engine class that implements all the required methods from `sensorthings.SensorThingsBaseEngine`. These methods will be used to map the SensorThings API to your data source.

After setting up your custom engine class, you can initialize the SensorThings API in your urls.py file:

```
from django.urls import path
from sensorthings import SensorThingsAPI
from .engine import YourCustomSensorThingsEngine


sta_core = SensorThingsAPI(
    title='Test SensorThings API',
    version='1.1',
    description='This is an example SensorThings API.',
    engine=YourCustomSensorThingsEngine
)

urlpatterns = [
    path('sensorthings/v1.1/', sta_core.urls),
]
```

To enable the SensorThings DataArray extension, your custom SensorThings should subclass `sensorthings.extensions.DataArrayBaseEngine` in addition to `sensorthings.SensorThingsBaseEngine`.

You can also modify specific SensorThings endpoints and components using `sensorthings.SensorThingsEndpoint` to add custom authorization rules, disable certain endpoints, or customize SensorThings properties schemas.

## Documentation

For detailed documentation on how to use HydroServer SensorThings, please refer to the [official documentation](https://hydroserver2.github.io/hydroserver-sensorthings/).

## Funding and Acknowledgements

Funding for this project was provided by the National Oceanic & Atmospheric Administration (NOAA), awarded to the Cooperative Institute for Research to Operations in Hydrology (CIROH) through the NOAA Cooperative Agreement with The University of Alabama (NA22NWS4320003).
