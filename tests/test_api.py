import os

import ecmwf.datastores.legacy_client
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

    assert os.path.getsize("test.grib") == 2076588


@pytest.mark.parametrize(
    "key,expected_client",
    [
        (
            ":",
            cdsapi.Client,
        ),
        (
            "",
            ecmwf.datastores.legacy_client.LegacyClient,
        ),
    ],
)
@pytest.mark.parametrize("key_from_env", [True, False])
def test_instantiation(monkeypatch, key, expected_client, key_from_env):
    if key_from_env:
        monkeypatch.setenv("CDSAPI_KEY", key)
        c = cdsapi.Client()
    else:
        c = cdsapi.Client(key=key)
    assert isinstance(c, cdsapi.Client)
    assert isinstance(c, expected_client)
    assert c.key == key
