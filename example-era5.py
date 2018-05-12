#!/usr/bin/env python

import cdsapi
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')


c = cdsapi.Client()


c.retrieve("reanalysis-era5-pressure-levels",
           {
               "variable": "temperature",
               "pressure_level": "1000",
               "product_type": "reanalysis",
               "date": "2008-01-01/2017-12-31",
               "time": "12:00",
               "format": "grib"
           },
           "dowload.grib")
