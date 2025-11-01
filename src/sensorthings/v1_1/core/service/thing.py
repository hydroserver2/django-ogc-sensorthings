from sensorthings.v1_1.core.dto import GroupedCollectionDTO, CollectionDTO, ThingDTO


class ThingService:
    def get_thing_collection(self, *args, **kwargs):

        thing = ThingDTO(
            iot_id=1,
            description="Test thing",
            iot_location_ids=[1, 2, 3],
            properties={"code": "A"},
        )

        thing.build_response(select=["iot_id", "description"])
        thing = {"iot_id": 1}

        collection = CollectionDTO(
            iot_count=1,
            value=[thing],
        )

        # collection.build_response()

        return collection

    def get_thing(self, *args, **kwargs) -> ThingDTO:

        thing = ThingDTO(
            iot_id=1,
            name="Test",
            description="Test thing",
            iot_location_ids=[1, 2, 3],
            properties={"code": "A"},
        )

        thing.apply_select_expand(
            select=["iot_id", "name"], expand={"locations": {"count": 12, "value": []}}
        )

        return thing
