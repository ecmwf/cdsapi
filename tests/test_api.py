import os
import pathlib
import re

import pytest
import requests_mock

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


def test_result_with_opened_target(tmp_path: pathlib.Path) -> None:
    """Tests whether a result can be downloaded in an opened target."""
    target_file = tmp_path / "test.grib"

    c = cdsapi.Client("https://example.com/", key="foo:bar")
    r = cdsapi.api.Result(c, {"message": "", "state": "completed", "location": "https://example.com/file", "content_length": 6})

    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, content=b"foobar")

        r.download(target_file)

    assert target_file.stat().st_size == 6


def test_result_with_io_target(tmp_path: pathlib.Path) -> None:
    """Tests whether a result can be downloaded directly into an IO target object."""
    target_file = tmp_path / "test.grib"

    c = cdsapi.Client("https://example.com/", key="foo:bar")
    r = cdsapi.api.Result(c, {"message": "", "state": "completed", "location": "https://example.com/file", "content_length": 6})

    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, content=b"foobar")

        with target_file.open("wb") as target:
            r.download(target)

    assert target_file.stat().st_size == 6


def test_invalid_target(tmp_path: pathlib.Path) -> None:
    """Tests whether a TypeError is raised for an unsupported target type."""
    target_file = tmp_path / "test.grib"

    with pytest.raises(TypeError, match=re.compile("invalid value for target", re.I)):
        with target_file.open("wt") as target:
            cdsapi.api._open_target(target)  # type: ignore[arg-type]


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
