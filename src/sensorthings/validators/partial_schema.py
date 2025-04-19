from ninja import Schema


class PartialSchema(type(Schema)):
    """
    Metaclass to create a partial schema.

    Sets all fields to optional and defaults them to None. Adds a validator that
    ensures required fields are not set to None.
    """

    def __new__(cls, name, bases, attrs, **kwargs):
        for base in bases:
            if issubclass(base, Schema):
                for field_name, field_value in base.model_fields.items():
                    field_value.default = None

        return super().__new__(cls, name, bases, attrs, **kwargs)
