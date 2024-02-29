import cads_api_client.legacy_api_client
import pytest

import cdsapi
import cdsapi.api


@pytest.mark.parametrize(
    "url,key,expected_client",
    [
        (
            None,
            None,
            cdsapi.api.Client,
        ),
        (
            "http://cds2-test.copernicus-climate.eu/api",
            "00000000-0000-4000-a000-000000000000",
            cads_api_client.legacy_api_client.LegacyApiClient,
        ),
    ],
)
def test_request(tmp_path, url, key, expected_client):
    c = cdsapi.Client(url=url, key=key)
    assert isinstance(c, expected_client)

    r = c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "variable": "2t",
            "product_type": "reanalysis",
            "date": "2012-12-01",
            "time": "12:00",
        },
    )

    target = tmp_path / "test.grib"
    r.download(str(target))

    assert target.stat().st_size == 2076600
