from datetime import datetime, timezone
import pytest
from sensorthings.versions.v1_1.backends.django.adapter import DjangoBackendAdapter
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


class TestNestedExpandNextLink:

    INNER_OBSERVATIONS = "Observations($orderby=result;$top=1)"

    @staticmethod
    def create_datastream(thing, name="Test Datastream", results=(1.0, 2.0, 3.0)):
        ds = create_test_datastream(thing=thing, name=name)
        for result in results:
            create_test_observation(result=result, datastream=ds)
        return ds

    @staticmethod
    def results(datastream):
        return [obs["result"] for obs in datastream["Observations"]]

    def assert_next_page(self, client, datastream):
        assert self.results(datastream) == [1.0]
        response = client.get(next_link_path(datastream["Observations@iot.nextLink"]))
        assert response.status_code == 200
        return response.json()

    def get_thing(self, client, thing, expand):
        response = client.get(f"/Things('{thing.id}')?$expand={expand}")
        assert response.status_code == 200
        return response.json()

    def test_two_level_expand(self, client):
        thing = create_test_thing()
        self.create_datastream(thing)
        body = self.get_thing(client, thing, f"Datastreams($expand={self.INNER_OBSERVATIONS})")
        page_two = self.assert_next_page(client, body["Datastreams"][0])
        assert self.results(page_two["Datastreams"][0]) == [2.0]

    def test_three_level_expand(self, client):
        thing = create_test_thing()
        location = create_test_location(things=[thing])
        self.create_datastream(thing)
        response = client.get(
            f"/Locations('{location.id}')?$expand=Things($expand=Datastreams($expand={self.INNER_OBSERVATIONS}))"
        )
        assert response.status_code == 200
        page_two = self.assert_next_page(client, response.json()["Things"][0]["Datastreams"][0])
        assert self.results(page_two["Things"][0]["Datastreams"][0]) == [2.0]

    def test_full_page_with_default_top(self, client):
        thing = create_test_thing()
        self.create_datastream(thing, results=[float(result) for result in range(100)])
        body = self.get_thing(client, thing, "Datastreams($expand=Observations)")
        datastream = body["Datastreams"][0]
        assert len(datastream["Observations"]) == 100
        assert "Observations($top=100;$skip=100)" in datastream["Observations@iot.nextLink"]

    def test_nested_filters_are_preserved(self, client):
        thing = create_test_thing()
        self.create_datastream(thing, name="semi;colon", results=(0.0, 1.0, 2.0))
        self.create_datastream(thing, name="Other")
        body = self.get_thing(
            client, thing,
            f"Datastreams($filter=contains(name,'semi;');"
            f"$expand=Observations($filter=result gt 0;$orderby=result;$top=1))"
        )
        assert [datastream["name"] for datastream in body["Datastreams"]] == ["semi;colon"]
        page_two = self.assert_next_page(client, body["Datastreams"][0])
        assert [datastream["name"] for datastream in page_two["Datastreams"]] == ["semi;colon"]
        assert self.results(page_two["Datastreams"][0]) == [2.0]

    def test_slash_form_inside_options(self, client):
        thing = create_test_thing()
        location = create_test_location(things=[thing])
        self.create_datastream(thing)
        response = client.get(
            f"/Locations('{location.id}')?$expand=Things($expand=Datastreams/{self.INNER_OBSERVATIONS})"
        )
        assert response.status_code == 200
        page_two = self.assert_next_page(client, response.json()["Things"][0]["Datastreams"][0])
        assert self.results(page_two["Things"][0]["Datastreams"][0]) == [2.0]

    @pytest.mark.parametrize("expand_template,sibling", [
        ("Datastreams($expand={inner},Sensor)", ",Sensor)"),
        ("Datastreams($expand={inner}),Locations($orderby=name)", ",Locations($orderby=name)"),
    ])
    def test_sibling_expands_are_preserved(self, client, expand_template, sibling):
        thing = create_test_thing()
        self.create_datastream(thing)
        expand = expand_template.format(inner=self.INNER_OBSERVATIONS)
        datastream = self.get_thing(client, thing, expand)["Datastreams"][0]
        assert sibling in datastream["Observations@iot.nextLink"]
        page_two = self.assert_next_page(client, datastream)
        assert self.results(page_two["Datastreams"][0]) == [2.0]

    def test_inner_and_outer_links_increment_only_their_own_skip(self, client):
        thing = create_test_thing()
        self.create_datastream(thing, name="A")
        self.create_datastream(thing, name="B", results=(10.0, 20.0))
        body = self.get_thing(
            client, thing, f"Datastreams($orderby=name;$top=1;$expand={self.INNER_OBSERVATIONS})"
        )
        inner_page = self.assert_next_page(client, body["Datastreams"][0])
        assert inner_page["Datastreams"][0]["name"] == "A"
        assert self.results(inner_page["Datastreams"][0]) == [2.0]

        outer_response = client.get(next_link_path(body["Datastreams@iot.nextLink"]))
        assert outer_response.status_code == 200
        outer_page = outer_response.json()
        assert outer_page["Datastreams"][0]["name"] == "B"
        assert self.results(outer_page["Datastreams"][0]) == [10.0]

    def test_slash_only_form_still_works(self, client):
        thing = create_test_thing()
        self.create_datastream(thing)
        body = self.get_thing(client, thing, f"Datastreams/{self.INNER_OBSERVATIONS}")
        page_two = self.assert_next_page(client, body["Datastreams"][0])
        assert self.results(page_two["Datastreams"][0]) == [2.0]


class TestNotEqualFilter:

    @staticmethod
    def thing_names(client, filter_option):
        response = client.get(f"/Things?$filter={filter_option}")
        assert response.status_code == 200
        return [thing["name"] for thing in response.json()["value"]]

    @pytest.mark.parametrize("filter_option,expected", [
        ("name ne 'Longer'", ["Alpha"]),
        ("not (name ne 'Longer')", ["Longer"]),
        ("name ne 'Alpha' and name ne 'Longer'", []),
        ("length(name) ne 5", ["Longer"]),
    ])
    def test_string_comparisons(self, client, filter_option, expected):
        create_test_thing(name="Alpha")
        create_test_thing(name="Longer")
        assert self.thing_names(client, filter_option) == expected

    def test_numeric_comparison(self, client):
        ds = create_test_datastream()
        create_test_observation(result=1.0, datastream=ds)
        create_test_observation(result=2.0, datastream=ds)
        body = client.get("/Observations?$filter=result ne 1.0").json()
        assert [obs["result"] for obs in body["value"]] == [2.0]

    def test_datetime_comparison(self, client):
        ds = create_test_datastream()
        create_test_observation(
            result=1.0, datastream=ds, phenomenon_time_begin=datetime(2020, 1, 1, tzinfo=timezone.utc)
        )
        create_test_observation(
            result=2.0, datastream=ds, phenomenon_time_begin=datetime(2021, 1, 1, tzinfo=timezone.utc)
        )
        body = client.get("/Observations?$filter=phenomenonTime ne 2020-01-01T00:00:00Z").json()
        assert [obs["result"] for obs in body["value"]] == [2.0]

    def test_related_entity_comparison(self, client):
        create_test_datastream(name="Keep", thing=create_test_thing(name="Alpha"))
        create_test_datastream(name="Drop", thing=create_test_thing(name="Beta"))
        body = client.get("/Datastreams?$filter=Thing/name ne 'Beta'").json()
        assert [ds["name"] for ds in body["value"]] == ["Keep"]

    def test_on_nested_path(self, client):
        ds = create_test_datastream()
        create_test_observation(result=1.0, datastream=ds)
        create_test_observation(result=2.0, datastream=ds)
        body = client.get(f"/Datastreams('{ds.id}')/Observations?$filter=result ne 1.0").json()
        assert [obs["result"] for obs in body["value"]] == [2.0]

    def test_inside_expand(self, client):
        thing = create_test_thing()
        create_test_datastream(thing=thing, name="Keep")
        create_test_datastream(thing=thing, name="Drop")
        body = client.get(f"/Things('{thing.id}')?$expand=Datastreams($filter=name ne 'Drop')").json()
        assert [ds["name"] for ds in body["Datastreams"]] == ["Keep"]


class TestInvalidQueryOptions:

    @pytest.mark.parametrize("path,message", [
        ("/Things?$filter=name eq", "Invalid $filter"),
        ("/Things?$filter=nofunc(name) eq 1", "Unknown function: 'nofunc'"),
        ("/Things?$filter=bogus eq 'x'", "Invalid $filter: unknown property"),
        ("/Things?$filter=name/foo eq 'x'", "Invalid $filter: unknown property"),
        ("/Things?$filter=name", "Invalid $filter: expression must be a boolean condition"),
        ("/Things?$filter=name lt null", "Cannot apply 'Lt' to 'null'"),
        ("/Things?$select=bogus", "Invalid fields in $select: bogus"),
        ("/Things?$orderby=bogus", "Invalid $orderby field path: 'bogus'"),
        ("/Things?$orderby=name sideways", "Invalid $orderby direction: 'name sideways'"),
        ("/Things?$expand=Bogus", "Invalid entity in $expand: Bogus"),
        ("/Things?$expand=Datastreams(", "must be balanced"),
        ("/Things('{id}')?$expand=Datastreams($bogus=1)", "Invalid option in $expand: $bogus"),
        ("/Things('{id}')?$expand=Datastreams($resultFormat=dataArray)", "Invalid option in $expand: $resultFormat"),
        ("/Things('{id}')?$expand=Datastreams($top=abc)", "Invalid $top in $expand: 'abc'"),
        ("/Things('{id}')?$expand=Datastreams($skip=abc)", "Invalid $skip in $expand: 'abc'"),
        ("/Things('{id}')?$expand=Datastreams($filter=name eq)", "Invalid $filter"),
        ("/Things('{id}')?$expand=Datastreams($filter=bogus eq 'x')", "Invalid $filter: unknown property"),
        ("/Things('{id}')/name?$top=1", "Query options are not allowed"),
    ])
    def test_returns_400_with_message(self, client, path, message):
        thing = create_test_thing()
        response = client.get(path.format(id=thing.id))
        assert response.status_code == 400
        assert message in response.json()["detail"]

    def test_unknown_property_does_not_list_model_fields(self, client):
        detail = client.get("/Things?$filter=bogus eq 'x'").json()["detail"]
        assert "Choices" not in detail
        assert "description" not in detail


class TestBackendErrors:

    @pytest.mark.parametrize("exception", [ValueError, TypeError])
    def test_exception_while_running_query_returns_500(self, client, monkeypatch, exception):
        def fail(self, **kwargs):
            raise exception("Backend failure")

        monkeypatch.setattr(DjangoBackendAdapter, "get_things", fail)
        response = client.get("/Things")
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"


class TestJsonPropertyFilter:

    PROPERTIES = {
        "camel": {
            "timeUnit": "days",
            "count": 5,
            "ratio": 1.5,
            "active": True,
            "nested": {"innerKey": "x"},
            "emptyValue": None,
            "note": "plain",
            "contains": "x",
            "phenomenonTime": "now",
        },
        "snake": {"time_unit": "days", "count": 0},
        "text": {"timeUnit": "hours", "count": "abc", "active": False, "nested": {"innerKey": "y"}},
        "numeric_text": {"count": "5"},
        "empty": {},
        "no_properties": None,
    }

    @classmethod
    def create_datastreams(cls, thing=None):
        for name, properties in cls.PROPERTIES.items():
            create_test_datastream(name=name, properties=properties, thing=thing)

    @pytest.mark.parametrize("filter_option,expected", [
        ("properties/timeUnit eq 'days'", ["camel"]),
        ("properties/time_unit eq 'days'", ["snake"]),
        ("properties/timeUnit ne 'days'", ["text"]),
        ("properties/count eq 5", ["camel"]),
        ("properties/count eq 'abc'", ["text"]),
        ("properties/count ne 5", ["numeric_text", "snake", "text"]),
        ("properties/count gt 1", ["camel", "numeric_text"]),
        ("properties/count ge 5", ["camel", "numeric_text"]),
        ("properties/count lt 1", ["snake"]),
        ("properties/count le 5", ["camel", "numeric_text", "snake"]),
        ("properties/ratio gt 1.0", ["camel"]),
        ("properties/note gt 'a'", ["camel"]),
        ("properties/active eq true", ["camel"]),
        ("properties/active eq false", ["text"]),
        ("properties/active ne true", ["text"]),
        ("properties/emptyValue eq null", ["camel", "empty", "no_properties", "numeric_text", "snake", "text"]),
        ("properties/emptyValue ne null", []),
        ("properties/timeUnit eq null", ["empty", "no_properties", "numeric_text", "snake"]),
        ("properties/timeUnit ne null", ["camel", "text"]),
        ("properties/missingKey ne 'x'", []),
        ("properties/nested/innerKey eq 'x'", ["camel"]),
        ("properties/contains eq 'x'", ["camel"]),
        ("properties/phenomenonTime eq 'now'", ["camel"]),
        ("properties/timeUnit eq 'days' and properties/count gt 1", ["camel"]),
        ("properties/timeUnit eq 'hours' or properties/count eq 5", ["camel", "text"]),
    ])
    def test_filter(self, client, filter_option, expected):
        self.create_datastreams()
        response = client.get(f"/Datastreams?$filter={filter_option}")
        assert response.status_code == 200
        assert sorted(ds["name"] for ds in response.json()["value"]) == expected

    def test_filter_through_related_entity(self, client):
        create_test_datastream(name="Keep", thing=create_test_thing(properties={"siteCode": "X"}))
        create_test_datastream(name="Drop", thing=create_test_thing(properties={"siteCode": "Y"}))
        body = client.get("/Datastreams?$filter=Thing/properties/siteCode eq 'X'").json()
        assert [ds["name"] for ds in body["value"]] == ["Keep"]

    def test_filter_inside_expand(self, client):
        thing = create_test_thing()
        self.create_datastreams(thing=thing)
        body = client.get(f"/Things('{thing.id}')?$expand=Datastreams($filter=properties/timeUnit eq 'days')").json()
        assert [ds["name"] for ds in body["Datastreams"]] == ["camel"]

    @pytest.mark.parametrize("filter_option,message", [
        ("properties/active gt true", "Cannot apply 'Gt' to 'Boolean'"),
        ("properties/count gt null", "Cannot apply 'Gt' to 'Null'"),
        ("properties/timeUnit eq 2020-01-01T00:00:00Z", "Cannot apply 'Eq' to 'DateTime'"),
        ("bogus/key eq 1", "unknown property"),
    ])
    def test_invalid_filter_returns_400(self, client, filter_option, message):
        response = client.get(f"/Datastreams?$filter={filter_option}")
        assert response.status_code == 400
        assert message in response.json()["detail"]
