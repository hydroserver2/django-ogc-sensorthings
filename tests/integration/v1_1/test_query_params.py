import pytest
from tests.factories.v1_1.django import (
    create_test_thing,
    create_test_datastream,
    create_test_observation,
)


pytestmark = pytest.mark.django_db


class TestFilterQuery:

    def test_filter_by_name_returns_matching_entity(self, client):
        create_test_thing(name="Alpha")
        create_test_thing(name="Beta")
        body = client.get("/Things?$filter=name eq 'Alpha'").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["name"] == "Alpha"

    def test_filter_no_match_returns_empty(self, client):
        create_test_thing(name="Alpha")
        body = client.get("/Things?$filter=name eq 'Nope'").json()
        assert body["value"] == []

    def test_filter_on_nested_path(self, client):
        ds = create_test_datastream()
        create_test_observation(result=1.0, datastream=ds)
        create_test_observation(result=2.0, datastream=ds)
        body = client.get(f"/Datastreams('{ds.id}')/Observations?$filter=result eq 1.0").json()
        assert len(body["value"]) == 1
        assert body["value"][0]["result"] == 1.0


class TestExpandQuery:

    def test_expand_collection_relationship(self, client):
        thing = create_test_thing()
        create_test_datastream(thing=thing)
        body = client.get(f"/Things('{thing.id}')?$expand=Datastreams").json()
        assert "Datastreams" in body
        assert len(body["Datastreams"]) == 1

    def test_expand_fk_relationship(self, client):
        ds = create_test_datastream()
        body = client.get(f"/Datastreams('{ds.id}')?$expand=Thing").json()
        assert "Thing" in body
        assert body["Thing"]["name"] == ds.thing.name

    def test_expand_replaces_nav_link(self, client):
        thing = create_test_thing()
        body = client.get(f"/Things('{thing.id}')?$expand=Datastreams").json()
        assert "Datastreams" in body
        assert "Datastreams@iot.navigationLink" not in body

    def test_unexpanded_relationships_remain_as_nav_links(self, client):
        thing = create_test_thing()
        body = client.get(f"/Things('{thing.id}')?$expand=Datastreams").json()
        assert "Locations@iot.navigationLink" in body

    def test_expand_on_collection(self, client):
        thing = create_test_thing()
        create_test_datastream(thing=thing)
        body = client.get("/Things?$expand=Datastreams").json()
        assert len(body["value"]) == 1
        assert "Datastreams" in body["value"][0]
        assert len(body["value"][0]["Datastreams"]) == 1

    def test_expand_empty_relationship(self, client):
        thing = create_test_thing()
        body = client.get(f"/Things('{thing.id}')?$expand=Datastreams").json()
        assert body["Datastreams"] == []
