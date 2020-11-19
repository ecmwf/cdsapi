import cdsapi
import os

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

    assert os.path.getsize("test.grib") == 2076600
