from datetime import datetime
from sensorthings.versions.v1_1 import Observation, Datastream, FeatureOfInterest
from .feature_of_interest import create_test_feature_of_interest
from .datastream import create_test_datastream


def create_test_observation(
    *,
    phenomenon_time_begin: datetime = datetime.utcnow(),
    phenomenon_time_end: datetime | None = None,
    result: float = 0.0,
    result_time: datetime = datetime.utcnow(),
    result_quality: dict | None = None,
    valid_time_begin: datetime | None = None,
    valid_time_end: datetime | None = None,
    parameters: dict | None = None,
    datastream: Datastream | None = None,
    feature_of_interest: FeatureOfInterest | None = None,
) -> Observation:
    """"""

    if datastream is None:
        datastream = create_test_datastream()

    if feature_of_interest is None:
        feature_of_interest = create_test_feature_of_interest()

    return Observation.objects.create(
        phenomenon_time_begin=phenomenon_time_begin,
        phenomenon_time_end=phenomenon_time_end,
        result=result,
        result_time=result_time,
        result_quality=result_quality,
        valid_time_begin=valid_time_begin,
        valid_time_end=valid_time_end,
        parameters=parameters,
        datastream=datastream,
        feature_of_interest=feature_of_interest,
    )
