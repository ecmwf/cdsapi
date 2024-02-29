import os

import cads_api_client.legacy_api_client
import pytest

import cdsapi


def test_request():
    c = cdsapi.Client()

    r = c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "variable": "2t",
            "product_type": "reanalysis",
            "date": "2012-12-01",
            "time": "12:00",
        },
    )

    r.download("test.grib")

    assert os.path.getsize("test.grib") == 2076600


@pytest.mark.parametrize(
    "key,expected_client",
    [
        (
            ":",
            cdsapi.Client,
        ),
        (
            "",
            cads_api_client.legacy_api_client.LegacyApiClient,
        ),
    ],
)
def test_instantiation(key, expected_client):
    c = cdsapi.Client(key=key)
    assert isinstance(c, cdsapi.Client)
    assert isinstance(c, expected_client)
