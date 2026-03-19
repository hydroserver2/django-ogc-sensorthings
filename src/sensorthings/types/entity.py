from dataclasses import dataclass, field


@dataclass(frozen=True)
class EntityType:
    name: str
    set_name: str
    primitive_properties: list[str] = field(default_factory=list)
    complex_properties: list[str] = field(default_factory=list)
    related_entity_type_names: list[str] = field(default_factory=list)
    related_entity_type_set_names: list[str] = field(default_factory=list)

    def __str__(self):
        return self.set_name

    @property
    def properties(self):
        return self.primitive_properties + self.complex_properties
