import pytest
from tests.factories.v1_1.django import (
    create_test_thing,
    create_test_datastream,
    create_test_observation,
    create_test_location,
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


def next_link_path(link):
    return link.split("/v1.1", 1)[1]


class TestExpandFilterQuery:

    @staticmethod
    def expanded_names(client, thing, options):
        response = client.get(f"/Things('{thing.id}')?$expand=Datastreams({options})")
        assert response.status_code == 200
        return sorted(ds["name"] for ds in response.json()["Datastreams"])

    def test_filter_limits_expanded_entities(self, client):
        ds = create_test_datastream()
        create_test_observation(result=-1.0, datastream=ds)
        create_test_observation(result=1.0, datastream=ds)
        body = client.get(f"/Datastreams('{ds.id}')?$expand=Observations($filter=result gt 0)").json()
        assert [obs["result"] for obs in body["Observations"]] == [1.0]

    def test_filter_combines_with_top_and_orderby(self, client):
        ds = create_test_datastream()
        for result in (-1.0, 1.0, 2.0, 3.0):
            create_test_observation(result=result, datastream=ds)
        body = client.get(
            f"/Datastreams('{ds.id}')?$expand=Observations($filter=result gt 0;$orderby=result;$top=2)"
        ).json()
        assert [obs["result"] for obs in body["Observations"]] == [1.0, 2.0]

    def test_filter_applies_per_parent(self, client):
        match = create_test_thing(name="Match")
        no_match = create_test_thing(name="No match")
        create_test_datastream(thing=match, name="Keep")
        create_test_datastream(thing=no_match, name="Drop")
        body = client.get("/Things?$expand=Datastreams($filter=name eq 'Keep')").json()
        expanded = {thing["name"]: [ds["name"] for ds in thing["Datastreams"]] for thing in body["value"]}
        assert expanded == {"Match": ["Keep"], "No match": []}

    def test_filter_on_many_to_many_relationship(self, client):
        thing = create_test_thing()
        create_test_location(name="Keep", things=[thing])
        create_test_location(name="Drop", things=[thing])
        body = client.get(f"/Things('{thing.id}')?$expand=Locations($filter=name eq 'Keep')").json()
        assert [location["name"] for location in body["Locations"]] == ["Keep"]

    def test_filter_in_nested_expand(self, client):
        thing = create_test_thing()
        ds = create_test_datastream(thing=thing, name="Keep")
        create_test_datastream(thing=thing, name="Drop")
        create_test_observation(result=1.0, datastream=ds)
        create_test_observation(result=5.0, datastream=ds)
        body = client.get(
            f"/Things('{thing.id}')?$expand=Datastreams($filter=name eq 'Keep';"
            f"$expand=Observations($filter=result gt 3))"
        ).json()
        assert [expanded["name"] for expanded in body["Datastreams"]] == ["Keep"]
        assert [obs["result"] for obs in body["Datastreams"][0]["Observations"]] == [5.0]

    @pytest.mark.parametrize("name", [
        "Discharge (cfs) - provisional",
        "semi;colon",
        "unmatched)close",
        "unmatched(open",
        "com,ma",
        "equals=sign",
        "sla/sh",
    ])
    def test_filter_string_with_reserved_characters(self, client, name):
        thing = create_test_thing()
        create_test_datastream(thing=thing, name=name)
        create_test_datastream(thing=thing, name="Other")
        assert self.expanded_names(client, thing, f"$filter=name eq '{name}'") == [name]

    def test_filter_string_with_escaped_quote(self, client):
        thing = create_test_thing()
        create_test_datastream(thing=thing, name="it's;here")
        create_test_datastream(thing=thing, name="Other")
        assert self.expanded_names(client, thing, "$filter=name eq 'it''s;here'") == ["it's;here"]

    def test_invalid_filter_returns_400(self, client):
        ds = create_test_datastream()
        response = client.get(f"/Datastreams('{ds.id}')?$expand=Observations($filter=result gt)")
        assert response.status_code == 400

    @pytest.mark.parametrize("prefix", ["Keep", "Keep;", "Keep/", "Keep,"])
    def test_next_link_preserves_filter(self, client, prefix):
        thing = create_test_thing()
        create_test_datastream(thing=thing, name=f"{prefix} 1")
        create_test_datastream(thing=thing, name=f"{prefix} 2")
        create_test_datastream(thing=thing, name="Other")
        first = client.get(
            f"/Things('{thing.id}')?$expand=Datastreams($filter=contains(name,'{prefix}');$orderby=name;$top=1)"
        ).json()
        assert [ds["name"] for ds in first["Datastreams"]] == [f"{prefix} 1"]
        second = client.get(next_link_path(first["Datastreams@iot.nextLink"]))
        assert second.status_code == 200
        assert [ds["name"] for ds in second.json()["Datastreams"]] == [f"{prefix} 2"]


class TestGroupedPagination:

    @staticmethod
    def create_observations():
        ds = create_test_datastream()
        for result in (1.0, 2.0, 3.0, 4.0):
            create_test_observation(result=result, datastream=ds)
        return ds

    def test_expand_skip_excludes_skipped_rows(self, client):
        ds = self.create_observations()
        body = client.get(
            f"/Datastreams('{ds.id}')?$expand=Observations($orderby=result;$skip=1;$top=2)"
        ).json()
        assert [obs["result"] for obs in body["Observations"]] == [2.0, 3.0]

    def test_expand_next_link_does_not_repeat_rows(self, client):
        ds = self.create_observations()
        first = client.get(f"/Datastreams('{ds.id}')?$expand=Observations($orderby=result;$top=2)").json()
        second = client.get(next_link_path(first["Observations@iot.nextLink"])).json()
        assert [obs["result"] for obs in first["Observations"]] == [1.0, 2.0]
        assert [obs["result"] for obs in second["Observations"]] == [3.0, 4.0]

    def test_navigation_path_skip_excludes_skipped_rows(self, client):
        ds = self.create_observations()
        body = client.get(f"/Datastreams('{ds.id}')/Observations?$orderby=result&$skip=1&$top=2").json()
        assert [obs["result"] for obs in body["value"]] == [2.0, 3.0]
