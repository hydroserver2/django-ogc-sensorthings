import orjson
from ninja.renderers import BaseRenderer


class SensorThingsRenderer(BaseRenderer):
    """
    A custom JSON renderer for the SensorThings API.

    This renderer checks if the request object has a pre-defined 'response_string' attribute.
    If so, it uses this string as the response. Otherwise, it defaults to the standard JSON rendering.
    """

    media_type = "application/json"

    def render(self, request, data, *, response_status):
        """
        Render the response for the given request and data.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.
        data : Any
            The data to render.
        response_status : int
            The HTTP response status.

        Returns
        -------
        str
            The rendered response string, either from 'response_string' attribute or standard JSON rendering.
        """

        return getattr(
            request,
            'response_string',
            orjson.dumps(data)
        )
