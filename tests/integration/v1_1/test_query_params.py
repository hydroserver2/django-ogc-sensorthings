from datetime import datetime, timezone
from urllib.parse import quote
import pytest
from sensorthings.versions.v1_1.backends.django.adapter import DjangoBackendAdapter
from tests.factories.v1_1.django import (
    create_test_thing,
    create_test_datastream,
    create_test_observation,
    create_test_location,
    create_test_sensor,
    create_test_observed_property,
    create_test_feature_of_interest,
    create_test_historical_location,
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
        ("bogus/key eq 1", "unknown property"),
    ])
    def test_invalid_filter_returns_400(self, client, filter_option, message):
        response = client.get(f"/Datastreams?$filter={filter_option}")
        assert response.status_code == 400
        assert message in response.json()["detail"]


class TestJsonFunctionFilter:

    PROPERTIES = {
        "plain": {
            "note": "plain",
            "otherNote": "pl",
            "nested": {"innerKey": "deep"},
            "count": 5,
            "ratio": 2.5,
            "when": "2020-03-04T05:06:07Z",
        },
        "other": {"note": "other", "count": 12, "when": "not-a-date"},
        "zed": {"note": "Zed"},
        "quote": {"note": 'pl"x'},
        "spaced": {"note": "  pad  "},
        "nonstr": {"note": 123},
        "offset": {"when": "2021-06-15T23:30:00+02:00"},
        "empty": {},
        "no_properties": None,
    }
    THING_PROPERTIES = {"siteName": "Alpha", "siteCount": 3, "meta": {"depth": 7}}

    @classmethod
    def create_datastreams(cls):
        thing = create_test_thing(properties=cls.THING_PROPERTIES)
        for name, properties in cls.PROPERTIES.items():
            create_test_datastream(name=name, properties=properties, thing=thing if name == "plain" else None)
        return thing

    @pytest.mark.parametrize("filter_option,expected", [
        # String functions
        ("length(properties/note) eq 5", ["other", "plain"]),
        ("length(properties/count) eq 1", ["plain"]),
        ("tolower(properties/note) eq 'zed'", ["zed"]),
        ("toupper(properties/note) eq 'ZED'", ["zed"]),
        ("trim(properties/note) eq 'pad'", ["spaced"]),
        ("startswith(properties/note,'pl')", ["plain", "quote"]),
        ("endswith(properties/note,'in')", ["plain"]),
        ("contains(properties/note,'la')", ["plain"]),
        ("contains(properties/note,'\"')", ["quote"]),
        ("contains(properties/note,'12')", ["nonstr"]),
        ("contains(properties/note,properties/otherNote)", ["plain"]),
        ("indexof(properties/note,'la') eq 1", ["plain"]),
        ("substring(properties/note,1) eq 'lain'", ["plain"]),
        ("substring(properties/note,1,2) eq 'la'", ["plain"]),
        ("matchesPattern(properties/note,'^pl')", ["plain", "quote"]),
        ("tolower(trim(properties/note)) eq 'pad'", ["spaced"]),
        ("startswith(tolower(properties/note),'z')", ["zed"]),
        # concat
        ("concat(properties/note,'x') eq 'plainx'", ["plain"]),
        ("concat('x',properties/note) eq 'xplain'", ["plain"]),
        ("concat(concat(properties/note,'-'),'x') eq 'plain-x'", ["plain"]),
        ("concat(name,'x') eq 'plainx'", ["plain"]),
        ("concat(description,'!') eq 'This is a datastream used for testing.!' and name eq 'plain'", ["plain"]),
        # Numeric functions
        ("round(properties/ratio) eq 3", ["plain"]),
        ("floor(properties/ratio) eq 2", ["plain"]),
        ("ceiling(properties/ratio) eq 3", ["plain"]),
        ("floor(properties/count) eq 5", ["plain"]),
        ("round(properties/note) eq 3", []),
        # Date functions
        ("year(properties/when) eq 2020", ["plain"]),
        ("month(properties/when) eq 3", ["plain"]),
        ("day(properties/when) eq 4", ["plain"]),
        ("hour(properties/when) eq 5", ["plain"]),
        ("minute(properties/when) eq 6", ["plain"]),
        ("second(properties/when) eq 7", ["plain"]),
        ("date(properties/when) eq 2020-03-04", ["plain"]),
        ("time(properties/when) eq 05:06:07", ["plain"]),
        ("year(properties/when) eq 2021", ["offset"]),
        ("hour(properties/when) eq 21", ["offset"]),
        ("year(properties/note) eq 2020", []),
        # Arithmetic
        ("properties/count add 1 eq 6", ["plain"]),
        ("properties/count sub 1 eq 4", ["plain"]),
        ("properties/ratio mul 2 eq 5.0", ["plain"]),
        ("properties/count add properties/ratio gt 7", ["plain"]),
        ("properties/note add 1 eq 2", []),
        # Functions on the right side of a comparison
        ("properties/note eq tolower('PLAIN')", ["plain"]),
        ("properties/note ne tolower('PLAIN')", ["nonstr", "other", "quote", "spaced", "zed"]),
        # Nested keys and related entities
        ("length(properties/nested/innerKey) eq 4", ["plain"]),
        ("startswith(properties/nested/innerKey,'de')", ["plain"]),
        ("length(Thing/properties/siteName) eq 5", ["plain"]),
        ("startswith(Thing/properties/siteName,'Al')", ["plain"]),
        ("concat(Thing/properties/siteName,'x') eq 'Alphax'", ["plain"]),
        ("Thing/properties/siteCount gt 1", ["plain"]),
        ("Thing/properties/siteCount lt 1", []),
        ("Thing/properties/siteName gt 'A'", ["plain"]),
        ("Thing/properties/meta/depth gt 1", ["plain"]),
        # Columns that are not JSON
        ("length(name) eq 13", ["no_properties"]),
        ("contains(name,'la')", ["plain"]),
    ])
    def test_filter(self, client, filter_option, expected):
        self.create_datastreams()
        response = client.get(f"/Datastreams?$filter={filter_option}")
        assert response.status_code == 200
        assert sorted(ds["name"] for ds in response.json()["value"]) == expected

    def test_function_on_whole_json_field_succeeds(self, client):
        self.create_datastreams()
        assert client.get("/Datastreams?$filter=length(properties) eq 1").status_code == 200

    def test_function_inside_expand(self, client):
        thing = self.create_datastreams()
        body = client.get(f"/Things('{thing.id}')?$expand=Datastreams($filter=length(properties/note) eq 5)").json()
        assert [ds["name"] for ds in body["Datastreams"]] == ["plain"]

    def test_date_function_on_column(self, client):
        ds = create_test_datastream()
        create_test_observation(
            result=1.0, datastream=ds, phenomenon_time_begin=datetime(2020, 1, 1, tzinfo=timezone.utc)
        )
        create_test_observation(
            result=2.0, datastream=ds, phenomenon_time_begin=datetime(2021, 1, 1, tzinfo=timezone.utc)
        )
        body = client.get("/Observations?$filter=year(phenomenonTime) eq 2020").json()
        assert [obs["result"] for obs in body["value"]] == [1.0]


class TestOrderBy:

    @staticmethod
    def create_datastreams():
        far = create_test_thing(properties={"siteCount": 30})
        near = create_test_thing(properties={"siteCount": 4})
        create_test_datastream(
            name="a", thing=near, properties={"sortKey": 2, "group": "y", "nested": {"rankKey": 30}}
        )
        create_test_datastream(
            name="b", thing=far, properties={"sortKey": 10, "group": "x", "nested": {"rankKey": 4}}
        )
        create_test_datastream(
            name="c", thing=far, properties={"sortKey": 1, "group": "y", "nested": {"rankKey": 100}}
        )
        return far

    @staticmethod
    def create_observations():
        ds = create_test_datastream()
        for result, year, rank in ((1.0, 2022, 2), (2.0, 2020, 10), (3.0, 2021, 1)):
            create_test_observation(
                result=result,
                datastream=ds,
                phenomenon_time_begin=datetime(year, 1, 1, tzinfo=timezone.utc),
                parameters={"rankKey": rank},
            )
        return ds

    @pytest.mark.parametrize("orderby,expected", [
        ("properties/sortKey", ["c", "a", "b"]),
        ("properties/sortKey desc", ["b", "a", "c"]),
        ("properties/nested/rankKey", ["b", "a", "c"]),
        ("properties/group,properties/sortKey", ["b", "c", "a"]),
        ("Thing/properties/siteCount desc,name", ["b", "c", "a"]),
    ])
    def test_datastreams(self, client, orderby, expected):
        self.create_datastreams()
        body = client.get(f"/Datastreams?$orderby={orderby}").json()
        assert [ds["name"] for ds in body["value"]] == expected

    def test_json_key_on_nested_path(self, client):
        thing = self.create_datastreams()
        body = client.get(f"/Things('{thing.id}')/Datastreams?$orderby=properties/sortKey").json()
        assert [ds["name"] for ds in body["value"]] == ["c", "b"]

    def test_json_key_inside_expand(self, client):
        thing = self.create_datastreams()
        body = client.get(f"/Things('{thing.id}')?$expand=Datastreams($orderby=properties/sortKey)").json()
        assert [ds["name"] for ds in body["Datastreams"]] == ["c", "b"]

    @pytest.mark.parametrize("orderby,expected", [
        ("phenomenonTime", [2.0, 3.0, 1.0]),
        ("phenomenonTime desc", [1.0, 3.0, 2.0]),
        ("parameters/rankKey", [3.0, 1.0, 2.0]),
        ("parameters/rankKey desc", [2.0, 1.0, 3.0]),
    ])
    def test_observations(self, client, orderby, expected):
        self.create_observations()
        body = client.get(f"/Observations?$orderby={orderby}").json()
        assert [obs["result"] for obs in body["value"]] == expected

    def test_valid_time_succeeds(self, client):
        self.create_observations()
        assert client.get("/Observations?$orderby=validTime").status_code == 200

    def test_phenomenon_time_inside_expand(self, client):
        ds = self.create_observations()
        body = client.get(f"/Datastreams('{ds.id}')?$expand=Observations($orderby=phenomenonTime)").json()
        assert [obs["result"] for obs in body["Observations"]] == [2.0, 3.0, 1.0]

    def test_phenomenon_time_with_data_array(self, client):
        self.create_observations()
        body = client.get("/Observations?$resultFormat=dataArray&$orderby=phenomenonTime&$select=result").json()
        assert body["value"][0]["dataArray"] == [[2.0], [3.0], [1.0]]


class TestKeywordPrefixedNames:

    KEYS = ["nullable", "nullValue", "null_x", "null1", "trueFlag", "truest", "falseFlag", "falsey", "anyone", "allowed"]

    @classmethod
    def create_datastreams(cls):
        thing = create_test_thing(name="Owner")
        create_test_datastream(
            name="match",
            thing=thing,
            properties={**{key: "x" for key in cls.KEYS}, "flag": True, "empty": None, "null": "x", "any": "x"},
        )
        create_test_datastream(name="other", thing=thing, properties={"flag": False})
        return thing

    @staticmethod
    def filtered_names(client, filter_option):
        response = client.get(f"/Datastreams?$filter={filter_option}")
        assert response.status_code == 200
        return sorted(ds["name"] for ds in response.json()["value"])

    @pytest.mark.parametrize("key", KEYS)
    def test_key_can_be_filtered(self, client, key):
        self.create_datastreams()
        assert self.filtered_names(client, f"properties/{key} eq 'x'") == ["match"]

    @pytest.mark.parametrize("filter_option,expected", [
        ("length(properties/nullable) eq 1", ["match"]),
        ("startswith(properties/allowed,'x')", ["match"]),
        ("properties/nullable eq 'x' and properties/flag eq true", ["match"]),
        ("properties/flag eq true and properties/trueFlag eq 'x'", ["match"]),
    ])
    def test_key_in_expression(self, client, filter_option, expected):
        self.create_datastreams()
        assert self.filtered_names(client, filter_option) == expected

    def test_key_inside_expand(self, client):
        thing = self.create_datastreams()
        body = client.get(f"/Things('{thing.id}')?$expand=Datastreams($filter=properties/nullable eq 'x')").json()
        assert [ds["name"] for ds in body["Datastreams"]] == ["match"]

    @pytest.mark.parametrize("lambda_filter", [
        "Datastreams/any(d:d/properties/nullable eq 'x')",
        "Datastreams/any(allVar:allVar/name eq 'match')",
    ])
    def test_name_inside_lambda(self, client, lambda_filter):
        self.create_datastreams()
        response = client.get(f"/Things?$filter={lambda_filter}")
        assert response.status_code == 200
        assert [thing["name"] for thing in response.json()["value"]] == ["Owner"]

    @pytest.mark.parametrize("filter_option,expected", [
        ("properties/flag eq true", ["match"]),
        ("properties/flag eq false", ["other"]),
        ("properties/empty eq null", ["match", "other"]),
        ("name ne null", ["match", "other"]),
    ])
    def test_literals_still_work(self, client, filter_option, expected):
        self.create_datastreams()
        assert self.filtered_names(client, filter_option) == expected

    @pytest.mark.parametrize("operator", ["any", "all"])
    def test_collection_operators_still_parse(self, client, operator):
        self.create_datastreams()
        assert client.get(f"/Things?$filter=Datastreams/{operator}(d:d/name eq 'match')").status_code == 200

    @pytest.mark.parametrize("key", ["null", "any"])
    def test_exact_keyword_key_is_rejected(self, client, key):
        self.create_datastreams()
        response = client.get(f"/Datastreams?$filter=properties/{key} eq 'x'")
        assert response.status_code == 400
        assert "Invalid $filter" in response.json()["detail"]


class TestCollectionOperators:

    @staticmethod
    def create_things():
        mixed = create_test_thing(name="mixed")
        create_test_datastream(thing=mixed, name="match")
        create_test_datastream(thing=mixed, name="other")
        all_match = create_test_thing(name="allmatch")
        create_test_datastream(thing=all_match, name="match")
        no_match = create_test_thing(name="nomatch")
        create_test_datastream(thing=no_match, name="other")
        create_test_thing(name="empty")
        create_test_location(name="Keep", things=[mixed, all_match])
        create_test_location(name="Drop", things=[mixed])
        return all_match, mixed

    @pytest.mark.parametrize("filter_option,expected", [
        ("Datastreams/all(d:d/name eq 'match')", ["allmatch", "empty"]),
        ("Datastreams/all(d:d/name ne 'match')", ["empty", "nomatch"]),
        ("Datastreams/any(d:d/name eq 'match')", ["allmatch", "mixed"]),
        ("not Datastreams/all(d:d/name eq 'match')", ["mixed", "nomatch"]),
        ("not Datastreams/any(d:d/name eq 'match')", ["empty", "nomatch"]),
        ("Datastreams/all(d:d/name eq 'match') and name eq 'allmatch'", ["allmatch"]),
        ("Datastreams/all(d:d/name eq 'match') or name eq 'nomatch'", ["allmatch", "empty", "nomatch"]),
        ("Datastreams/all(d:d/name eq 'match') and Datastreams/any()", ["allmatch"]),
        ("Datastreams/all(d:contains(d/name,'mat'))", ["allmatch", "empty"]),
        ("Datastreams/all(d:d/Thing/name eq 'allmatch')", ["allmatch", "empty"]),
        ("Locations/all(l:l/name eq 'Keep')", ["allmatch", "empty", "nomatch"]),
    ])
    def test_filter(self, client, filter_option, expected):
        self.create_things()
        response = client.get(f"/Things?$filter={filter_option}")
        assert response.status_code == 200
        assert sorted(thing["name"] for thing in response.json()["value"]) == expected

    def test_all_inside_expand(self, client):
        self.create_things()
        body = client.get(
            "/Locations?$filter=name eq 'Keep'&$expand=Things($filter=Datastreams/all(d:d/name eq 'match'))"
        ).json()
        assert [thing["name"] for thing in body["value"][0]["Things"]] == ["allmatch"]


class TestToOneExpand:

    EXPECTED = {
        "D0": {"Thing": "T0", "Sensor": "S0", "ObservedProperty": "P0"},
        "D1": {"Thing": "T1", "Sensor": "S1", "ObservedProperty": "P1"},
        "D2": {"Thing": "T2", "Sensor": "S2", "ObservedProperty": "P2"},
        "D3": {"Thing": "T0", "Sensor": "S1", "ObservedProperty": "P2"},
    }

    @classmethod
    def create_datastreams(cls):
        things = {name: create_test_thing(name=name) for name in ("T0", "T1", "T2")}
        sensors = {name: create_test_sensor(name=name) for name in ("S0", "S1", "S2")}
        properties = {name: create_test_observed_property(name=name) for name in ("P0", "P1", "P2")}
        datastreams = {
            name: create_test_datastream(
                name=name,
                thing=things[related["Thing"]],
                sensor=sensors[related["Sensor"]],
                observed_property=properties[related["ObservedProperty"]],
            )
            for name, related in cls.EXPECTED.items()
        }
        return things, datastreams

    @classmethod
    def assert_related(cls, datastreams, *relations):
        assert datastreams
        for datastream in datastreams:
            for relation in relations:
                assert datastream[relation]["name"] == cls.EXPECTED[datastream["name"]][relation]

    def test_each_row_gets_its_own_entities(self, client):
        self.create_datastreams()
        body = client.get("/Datastreams?$expand=Thing,Sensor,ObservedProperty").json()
        self.assert_related(body["value"], "Thing", "Sensor", "ObservedProperty")

    def test_with_select(self, client):
        self.create_datastreams()
        body = client.get("/Datastreams?$select=id,name&$expand=Thing($select=id,name),Sensor($select=id,name)").json()
        self.assert_related(body["value"], "Thing", "Sensor")

    def test_with_select_without_id(self, client):
        self.create_datastreams()
        body = client.get("/Datastreams?$select=name&$expand=Thing($select=name)").json()
        self.assert_related(body["value"], "Thing")

    def test_on_nested_path(self, client):
        things, _ = self.create_datastreams()
        body = client.get(f"/Things('{things['T0'].id}')/Datastreams?$expand=ObservedProperty").json()
        self.assert_related(body["value"], "ObservedProperty")

    @pytest.mark.parametrize("expand", [
        "Datastreams($expand=Sensor,ObservedProperty)",
        "Datastreams/Sensor",
    ])
    def test_inside_to_many_expand(self, client, expand):
        self.create_datastreams()
        relations = ["Sensor", "ObservedProperty"] if "ObservedProperty" in expand else ["Sensor"]
        body = client.get(f"/Things?$expand={expand}").json()
        self.assert_related([ds for thing in body["value"] for ds in thing["Datastreams"]], *relations)

    def test_to_many_inside_to_one_expand(self, client):
        self.create_datastreams()
        body = client.get("/Datastreams?$expand=Thing($expand=Datastreams($orderby=name))").json()
        by_thing = {"T0": ["D0", "D3"], "T1": ["D1"], "T2": ["D2"]}
        for datastream in body["value"]:
            thing = datastream["Thing"]
            assert thing["name"] == self.EXPECTED[datastream["name"]]["Thing"]
            assert [nested["name"] for nested in thing["Datastreams"]] == by_thing[thing["name"]]

    def test_observations(self, client):
        _, datastreams = self.create_datastreams()
        features = [create_test_feature_of_interest(name=name) for name in ("F0", "F1")]
        create_test_observation(result=1.0, datastream=datastreams["D0"], feature_of_interest=features[0])
        create_test_observation(result=2.0, datastream=datastreams["D1"], feature_of_interest=features[1])
        body = client.get("/Observations?$orderby=result&$expand=Datastream,FeatureOfInterest").json()
        assert [(obs["Datastream"]["name"], obs["FeatureOfInterest"]["name"]) for obs in body["value"]] == [
            ("D0", "F0"),
            ("D1", "F1"),
        ]

    def test_historical_locations(self, client):
        things, _ = self.create_datastreams()
        for year, name in ((2020, "T0"), (2021, "T1")):
            create_test_historical_location(thing=things[name], time=datetime(year, 1, 1, tzinfo=timezone.utc))
        body = client.get("/HistoricalLocations?$orderby=time&$expand=Thing").json()
        assert [location["Thing"]["name"] for location in body["value"]] == ["T0", "T1"]

    def test_filter_only_attaches_to_matching_rows(self, client):
        self.create_datastreams()
        body = client.get("/Datastreams?$expand=Thing($filter=name eq 'T1')").json()
        expanded = {ds["name"]: ds.get("Thing", {}).get("name") for ds in body["value"]}
        assert expanded == {"D0": None, "D1": "T1", "D2": None, "D3": None}

    def test_top_does_not_limit_related_entities(self, client):
        self.create_datastreams()
        body = client.get("/Datastreams?$expand=Thing($top=1)").json()
        self.assert_related(body["value"], "Thing")

    def test_count_is_not_added(self, client):
        self.create_datastreams()
        body = client.get("/Datastreams?$expand=Thing($count=true)").json()
        self.assert_related(body["value"], "Thing")
        assert not any("Thing@iot.count" in datastream for datastream in body["value"])

    def test_single_entity(self, client):
        _, datastreams = self.create_datastreams()
        body = client.get(f"/Datastreams('{datastreams['D1'].id}')?$expand=Thing,Sensor").json()
        self.assert_related([body], "Thing", "Sensor")

    def test_to_many_expand_is_unchanged(self, client):
        self.create_datastreams()
        body = client.get("/Things?$orderby=name&$expand=Datastreams($orderby=name;$count=true)").json()
        assert [
            (thing["name"], [ds["name"] for ds in thing["Datastreams"]], thing["Datastreams@iot.count"])
            for thing in body["value"]
        ] == [("T0", ["D0", "D3"], 2), ("T1", ["D1"], 1), ("T2", ["D2"], 1)]


class TestInvalidFilterExpressions:

    @pytest.mark.parametrize("filter_option,message", [
        ("year(name) eq 2020", "Invalid $filter: invalid function argument"),
        ("name add 1 gt 2", "Invalid $filter: unknown property or incompatible types"),
        ("name/a/b eq 1", "Invalid $filter: unknown property or incompatible types"),
    ])
    def test_returns_400(self, client, filter_option, message):
        response = client.get(f"/Things?$filter={filter_option}")
        assert response.status_code == 400
        assert response.json()["detail"] == message


class TestJsonLiteralFilter:

    INSTANT = "2024-06-01T00:00:00Z"

    @staticmethod
    def create_datastreams():
        create_test_datastream(name="A", properties={"depth": 5, "code": "x", "day": "2024-06-01", "at": "2024-06-01T00:00:00Z"})
        create_test_datastream(name="B", properties={"depth": 9, "code": "y", "day": "2023-06-01", "at": "2024-06-01T02:00:00+02:00"})
        create_test_datastream(name="C", properties={"depth": 7, "code": "z", "day": "2025-06-01", "at": "2025-06-01T00:00:00Z"})
        create_test_datastream(name="D", properties={"at": "not-a-date"})

    @pytest.mark.parametrize("filter_option,expected", [
        ("properties/depth in (5,9)", ["A", "B"]),
        ("properties/code in ('y','z')", ["B", "C"]),
        ("properties/depth in (5,null)", ["A", "D"]),
        (f"properties/at eq {INSTANT}", ["A", "B"]),
        (f"properties/at ne {INSTANT}", ["C"]),
        (f"properties/at gt {INSTANT}", ["C"]),
        (f"properties/at ge {INSTANT}", ["A", "B", "C"]),
        (f"properties/at lt {INSTANT}", []),
        ("properties/day gt 2024-01-01", ["A", "C"]),
        ("properties/day eq 2024-06-01", ["A"]),
    ])
    def test_filter(self, client, filter_option, expected):
        self.create_datastreams()
        response = client.get(f"/Datastreams?$filter={filter_option}")
        assert response.status_code == 200
        assert sorted(ds["name"] for ds in response.json()["value"]) == expected


class TestManyToManyGrouping:

    @staticmethod
    def create_things():
        first, second, third = (create_test_thing(name=name) for name in ("A", "B", "C"))
        create_test_location(name="L1", things=[first, second])
        create_test_location(name="L2", things=[first, third])
        return first, second, third

    @staticmethod
    def expanded(body):
        return {thing["name"]: [location["name"] for location in thing["Locations"]] for thing in body["value"]}

    def test_expand_has_no_duplicates(self, client):
        self.create_things()
        body = client.get("/Things?$expand=Locations($orderby=name)").json()
        assert self.expanded(body) == {"A": ["L1", "L2"], "B": ["L1"], "C": ["L2"]}

    def test_expand_paginates_each_parent(self, client):
        self.create_things()
        body = client.get("/Things?$expand=Locations($orderby=name;$skip=1)").json()
        assert self.expanded(body) == {"A": ["L2"], "B": [], "C": []}

    def test_nested_path_has_no_duplicates(self, client):
        _, second, _ = self.create_things()
        body = client.get(f"/Things('{second.id}')/Locations").json()
        assert [location["name"] for location in body["value"]] == ["L1"]

    def test_expand_historical_locations(self, client):
        thing = create_test_thing()
        location = create_test_location(name="L1", things=[thing])
        historical_location = create_test_historical_location(thing=thing, locations=[location])
        response = client.get("/Locations?$expand=HistoricalLocations")
        assert response.status_code == 200
        assert [
            entity["@iot.id"] for entity in response.json()["value"][0]["HistoricalLocations"]
        ] == [str(historical_location.id)]

    def test_nested_historical_locations(self, client):
        thing = create_test_thing()
        location = create_test_location(name="L1", things=[thing])
        historical_location = create_test_historical_location(thing=thing, locations=[location])
        body = client.get(f"/Locations('{location.id}')/HistoricalLocations").json()
        assert [entity["@iot.id"] for entity in body["value"]] == [str(historical_location.id)]


class TestDatastreamResultTime:

    @staticmethod
    def create_datastreams():
        create_test_datastream(name="Old", result_time_begin=datetime(2019, 1, 1, tzinfo=timezone.utc))
        create_test_datastream(name="New", result_time_begin=datetime(2021, 1, 1, tzinfo=timezone.utc))

    def test_filter(self, client):
        self.create_datastreams()
        response = client.get("/Datastreams?$filter=resultTime gt 2020-01-01T00:00:00Z")
        assert response.status_code == 200
        assert [ds["name"] for ds in response.json()["value"]] == ["New"]

    def test_orderby(self, client):
        self.create_datastreams()
        response = client.get("/Datastreams?$orderby=resultTime asc")
        assert response.status_code == 200
        assert [ds["name"] for ds in response.json()["value"]] == ["Old", "New"]

    def test_observation_result_time_is_unchanged(self, client):
        create_test_observation(result=1.0, result_time=datetime(2019, 1, 1, tzinfo=timezone.utc))
        create_test_observation(result=2.0, result_time=datetime(2021, 1, 1, tzinfo=timezone.utc))
        body = client.get("/Observations?$filter=resultTime gt 2020-01-01T00:00:00Z").json()
        assert [observation["result"] for observation in body["value"]] == [2.0]


class TestExpandOptionValues:

    @pytest.mark.parametrize("options,message", [
        ("$top=-1", "Invalid $top in $expand: '-1'"),
        ("$top=101", "Invalid $top in $expand: '101'"),
        ("$skip=-1", "Invalid $skip in $expand: '-1'"),
        ("$count=maybe", "Invalid $count in $expand: 'maybe'"),
        ("top=1", "Invalid option in $expand: top"),
        ("expand=Observations($top=1)", "Invalid option in $expand: expand"),
    ])
    def test_invalid_option_returns_400(self, client, options, message):
        response = client.get(f"/Things?$expand=Datastreams({options})")
        assert response.status_code == 400
        assert response.json()["detail"] == message

    def test_top_at_limit_is_allowed(self, client):
        create_test_thing()
        assert client.get("/Things?$expand=Datastreams($top=100)").status_code == 200

    @pytest.mark.parametrize("value,expected", [("true", True), ("false", False)])
    def test_count(self, client, value, expected):
        create_test_datastream()
        body = client.get(f"/Things?$expand=Datastreams($count={value})").json()
        assert ("Datastreams@iot.count" in body["value"][0]) is expected


class TestNextLinkEncoding:

    @staticmethod
    def follow(client, link):
        return client.get(link.split("/v1.1", 1)[1])

    @pytest.mark.parametrize("literal", ["a&b", "a+b", "a#b", "a%b"])
    def test_collection_next_link(self, client, literal):
        for name in ("A", "B"):
            create_test_thing(name=name)
        body = client.get("/Things", data={"$filter": f"name ne '{literal}'", "$orderby": "name", "$top": 1}).json()
        assert quote(literal) in body["@iot.nextLink"]
        next_page = self.follow(client, body["@iot.nextLink"])
        assert next_page.status_code == 200
        assert [thing["name"] for thing in next_page.json()["value"]] == ["B"]

    @pytest.mark.parametrize("literal", ["a&b", "a+b", "a#b", "a%b"])
    def test_expand_next_link(self, client, literal):
        thing = create_test_thing()
        for name in ("A", "B"):
            create_test_datastream(thing=thing, name=name)
        expand = f"Datastreams($top=1;$orderby=name;$filter=name ne '{literal}')"
        body = client.get(f"/Things('{thing.id}')", data={"$expand": expand}).json()
        assert quote(literal) in body["Datastreams@iot.nextLink"]
        next_page = self.follow(client, body["Datastreams@iot.nextLink"])
        assert next_page.status_code == 200
        assert [ds["name"] for ds in next_page.json()["Datastreams"]] == ["B"]


class TestJsonComparisonOperands:

    @staticmethod
    def create_datastreams(thing=None):
        create_test_datastream(
            thing=thing,
            name="Alpha",
            phenomenon_time_begin=datetime(2021, 1, 1, tzinfo=timezone.utc),
            properties={"depth": 5, "year": 2021, "label": "alpha", "at": "2021-06-01T00:00:00Z", "day": "2021-01-01"},
        )
        create_test_datastream(
            thing=thing,
            name="Beta",
            phenomenon_time_begin=datetime(2019, 1, 1, tzinfo=timezone.utc),
            properties={"depth": 9, "year": 2023, "label": "Beta", "at": "2018-06-01T00:00:00Z", "day": "2020-01-01"},
        )
        create_test_datastream(thing=thing, name="Text", properties={"depth": "not-a-number", "at": "not-a-date"})

    @pytest.mark.parametrize("filter_option,expected", [
        ("5 eq properties/depth", ["Alpha"]),
        ("5 ne properties/depth", ["Beta", "Text"]),
        ("6 lt properties/depth", ["Beta"]),
        ("6 ge properties/depth", ["Alpha"]),
        ("properties/depth eq 2 add 3", ["Alpha"]),
        ("2 add 3 eq properties/depth", ["Alpha"]),
        ("properties/year eq year(phenomenonTime)", ["Alpha"]),
        ("year(phenomenonTime) eq properties/year", ["Alpha"]),
        ("properties/depth eq length(name)", ["Alpha"]),
        ("properties/label eq name", ["Beta"]),
        ("name eq properties/label", ["Beta"]),
        ("properties/label eq tolower('ALPHA')", ["Alpha"]),
        ("properties/at gt phenomenonTime", ["Alpha"]),
        ("phenomenonTime lt properties/at", ["Alpha"]),
        ("properties/depth eq properties/depth", ["Alpha", "Beta", "Text"]),
        ("properties/label eq id", []),
    ])
    def test_filter(self, client, filter_option, expected):
        self.create_datastreams()
        response = client.get(f"/Datastreams?$filter={filter_option}")
        assert response.status_code == 200
        assert sorted(ds["name"] for ds in response.json()["value"]) == expected

    def test_date_function(self, client):
        self.create_datastreams()
        response = client.get("/Datastreams?$filter=properties/day eq date(phenomenonTime)")
        assert response.status_code == 200
        assert [ds["name"] for ds in response.json()["value"]] == ["Alpha"]

    @pytest.mark.parametrize("filter_option", [
        "result lt Datastream/properties/depth",
        "Datastream/properties/depth gt result",
    ])
    def test_numeric_column_through_relation(self, client, filter_option):
        datastream = create_test_datastream(properties={"depth": 5})
        create_test_observation(datastream=datastream, result=1.0)
        create_test_observation(datastream=datastream, result=6.0)
        response = client.get(f"/Observations?$filter={filter_option}")
        assert response.status_code == 200
        assert [observation["result"] for observation in response.json()["value"]] == [1.0]

    @pytest.mark.parametrize("filter_option", [
        "Datastreams/any(d:d/properties/depth eq 5)",
        "Datastreams/any(d:5 eq d/properties/depth)",
    ])
    def test_inside_collection_operator(self, client, filter_option):
        keep = create_test_thing(name="Keep")
        self.create_datastreams(thing=keep)
        create_test_datastream(thing=create_test_thing(name="Drop"), properties={"depth": 1})
        response = client.get(f"/Things?$filter={filter_option}")
        assert response.status_code == 200
        assert [thing["name"] for thing in response.json()["value"]] == ["Keep"]

    def test_invalid_reversed_in_returns_400(self, client):
        response = client.get("/Datastreams?$filter=5 in properties/depth")
        assert response.status_code == 400


class TestGroupedQueryOptions:

    @staticmethod
    def create_related():
        things = {name: create_test_thing(name=name) for name in ("A", "B", "C")}
        locations = {
            "L1": create_test_location(name="L1", things=[things["A"], things["B"]]),
            "L2": create_test_location(name="L2", things=[things["A"], things["C"]]),
        }
        return things, locations

    @staticmethod
    def expanded(body, relation="Locations"):
        return {
            thing["name"]: ([entity["name"] for entity in thing[relation]], thing.get(f"{relation}@iot.count"))
            for thing in body["value"]
        }

    @staticmethod
    def names(body):
        return [entity["name"] for entity in body["value"]]

    def test_nested_filter_through_grouping_relation(self, client):
        things, _ = self.create_related()
        body = client.get(f"/Things('{things['B'].id}')/Locations?$filter=Things/name eq 'A'&$count=true").json()
        assert self.names(body) == ["L1"]
        assert body["@iot.count"] == 1

    def test_reverse_nested_filter_through_grouping_relation(self, client):
        _, locations = self.create_related()
        body = client.get(f"/Locations('{locations['L1'].id}')/Things?$filter=Locations/name eq 'L2'").json()
        assert self.names(body) == ["A"]

    def test_expand_filter_through_grouping_relation(self, client):
        self.create_related()
        body = client.get("/Things?$expand=Locations($filter=Things/name eq 'B';$count=true;$orderby=name)").json()
        assert self.expanded(body) == {"A": (["L1"], 1), "B": (["L1"], 1), "C": ([], 0)}

    def test_filter_matching_several_related_rows_has_no_duplicates(self, client):
        things, _ = self.create_related()
        body = client.get(f"/Things('{things['B'].id}')/Locations?$filter=Things/name ne 'Z'&$count=true").json()
        assert self.names(body) == ["L1"]
        assert body["@iot.count"] == 1

    def test_expand_count_respects_filter(self, client):
        self.create_related()
        body = client.get("/Things?$expand=Locations($filter=name eq 'L1';$count=true)").json()
        assert self.expanded(body) == {"A": (["L1"], 1), "B": (["L1"], 1), "C": ([], 0)}

    def test_expand_count_ignores_page_size(self, client):
        self.create_related()
        body = client.get("/Things?$expand=Locations($top=1;$count=true;$orderby=name)").json()
        assert self.expanded(body) == {"A": (["L1"], 2), "B": (["L1"], 1), "C": (["L2"], 1)}

    def test_expand_select(self, client):
        self.create_related()
        body = client.get("/Things?$expand=Locations($select=name;$orderby=name)").json()
        assert self.expanded(body) == {"A": (["L1", "L2"], None), "B": (["L1"], None), "C": (["L2"], None)}
        assert all(set(location) == {"name"} for thing in body["value"] for location in thing["Locations"])

    def test_reverse_nested_count(self, client):
        _, locations = self.create_related()
        body = client.get(f"/Locations('{locations['L1'].id}')/Things?$count=true&$orderby=name").json()
        assert self.names(body) == ["A", "B"]
        assert body["@iot.count"] == 2

    def test_reverse_nested_pagination(self, client):
        _, locations = self.create_related()
        body = client.get(f"/Locations('{locations['L1'].id}')/Things?$top=1&$skip=1&$orderby=name").json()
        assert self.names(body) == ["B"]

    def test_foreign_key_default_order_is_newest_first(self, client):
        thing = create_test_thing()
        ids = [str(create_test_datastream(thing=thing).id) for _ in range(3)]
        body = client.get(f"/Things('{thing.id}')?$expand=Datastreams").json()
        assert [datastream["@iot.id"] for datastream in body["Datastreams"]] == sorted(ids, reverse=True)

    def test_many_to_many_default_order_is_newest_first(self, client):
        thing = create_test_thing()
        ids = [str(create_test_location(things=[thing]).id) for _ in range(3)]
        body = client.get(f"/Things('{thing.id}')?$expand=Locations").json()
        assert [location["@iot.id"] for location in body["Locations"]] == sorted(ids, reverse=True)

    def test_foreign_key_rows_keep_parent_when_interleaved(self, client):
        things = [create_test_thing(name=name) for name in ("A", "B")]
        for index, thing in enumerate(things * 2):
            create_test_datastream(thing=thing, name=f"D{index}")
        body = client.get("/Things?$expand=Datastreams($orderby=name;$top=1;$count=true)").json()
        assert self.expanded(body, "Datastreams") == {"A": (["D0"], 2), "B": (["D1"], 2)}
