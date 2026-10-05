from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from cdsapi.api import Client, Result


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        requests.Session,
        "request",
        Mock(side_effect=AssertionError("Unexpected HTTP request")),
    )
    with requests.Session() as session:
        yield Client(
            url="https://example.invalid/api/",
            key="test:token",
            session=session,
            quiet=True,
            delete=False,
        )


@pytest.fixture
def download(monkeypatch):
    download = Mock(
        side_effect=lambda url, size, target: (
            url.rsplit("/", 1)[-1] if target is None else target
        )
    )
    monkeypatch.setattr(Result, "_download", download)
    return download


def make_result(client, name, as_dict):
    if as_dict:
        return {"location": name, "contentLength": 1, "contentType": "test"}
    return Result(
        client,
        {"location": name, "content_length": 1, "content_type": "test"},
    )


@pytest.mark.parametrize("as_dict", [False, True])
@pytest.mark.parametrize(
    "targets,expected",
    [
        ("download.nc", "download.nc"),
        (b"download.nc", b"download.nc"),
        (Path("download.nc"), Path("download.nc")),
        (["download.nc"], "download.nc"),
        (("download.nc",), "download.nc"),
        (None, "source.nc"),
        ([], "source.nc"),
    ],
)
def test_download_single_result(client, download, as_dict, targets, expected):
    result = make_result(client, "source.nc", as_dict)
    original = targets.copy() if isinstance(targets, list) else targets

    assert client.download(result, targets) == expected

    assert targets == original
    target = None if not targets else expected
    download.assert_called_once_with("https://example.invalid/api/source.nc", 1, target)


@pytest.mark.parametrize("as_dict", [False, True])
@pytest.mark.parametrize("result_type", [list, tuple])
@pytest.mark.parametrize("target_type", [list, tuple])
def test_download_multiple_results(client, download, as_dict, result_type, target_type):
    results = result_type(
        make_result(client, name, as_dict) for name in ("a.nc", "b.nc")
    )
    targets = target_type(("first.nc", "second.nc"))

    assert client.download(results, targets) == ["first.nc", "second.nc"]

    assert list(targets) == ["first.nc", "second.nc"]
    assert download.call_count == 2


@pytest.mark.parametrize("target_type", [str, bytes, Path])
def test_download_writes_target(client, tmp_path, target_type):
    path = tmp_path / "download.nc"
    target = bytes(path) if target_type is bytes else target_type(path)
    payload = b"offline download payload"
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.reason = "OK"
    response.iter_content.return_value = [payload]
    client.session.get = Mock(return_value=response)
    result = Result(
        client,
        {
            "location": "source.nc",
            "content_length": len(payload),
            "content_type": "test",
        },
    )

    assert client.download(result, target) == target

    assert path.read_bytes() == payload
    response.close.assert_called_once_with()
    client.session.get.assert_called_once_with(
        "https://example.invalid/api/source.nc",
        stream=True,
        verify=client.verify,
        headers=None,
        timeout=client.timeout,
    )
