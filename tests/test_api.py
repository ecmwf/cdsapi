from __future__ import absolute_import, division, print_function, unicode_literals

import cdsapi


def test_request():

    c = cdsapi.Client()

    r = c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "variable": "2t",
            "product_type": "reanalysis",
            "date": "2012-12-01",
            "time": "12:00"
        },
    )

    r.download("test.grib")
