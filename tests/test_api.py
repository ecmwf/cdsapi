
from __future__ import absolute_import, division, print_function, unicode_literals

from cdsapi import api


def test_bytes_to_string():
    assert api.bytes_to_string(1) == '1'
    assert api.bytes_to_string(1 << 10) == '1K'
    assert api.bytes_to_string(1 << 20) == '1M'
    assert api.bytes_to_string(1 << 30) == '1G'
    assert api.bytes_to_string(1 << 40) == '1T'
    assert api.bytes_to_string(1 << 50) == '1P'
