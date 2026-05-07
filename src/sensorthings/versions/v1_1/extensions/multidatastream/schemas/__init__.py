from .multi_datastream import MultiDatastreamFields


def __getattr__(name: str):
    """Lazily resolve MultiDatastream schemas from the shared factory cache.

    Schemas are built by the MultiDatastream extension's `ready()` method. Any
    import of these names before that method runs will raise `AttributeError`.
    """

    from sensorthings.versions.v1_1.schemas import schema_factory

    try:
        if name == "MultiDatastreamResponse":
            return schema_factory._response_cache["MultiDatastream"]
        if name == "MultiDatastreamCollectionResponse":
            return schema_factory._collection_cache["MultiDatastream"]
        if name == "MultiDatastreamPostBody":
            return schema_factory._post_body_cache[("MultiDatastream", frozenset())]
        if name == "MultiDatastreamPatchBody":
            return schema_factory._patch_body_cache["MultiDatastream"]
    except KeyError:
        raise AttributeError(
            f"Schema {name!r} is not yet available. "
            f"Ensure the MultiDatastream extension's ready() has run before importing schemas."
        )

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
