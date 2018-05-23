#!/usr/bin/env python

# (C) Copyright 2018 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import cdsapi
import logging


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


c = cdsapi.Client()


c.retrieve("reanalysis-era5-pressure-levels",
           {
               "variable": "temperature",
               "pressure_level": "250",
               "product_type": "reanalysis",
               "date": "2017-12-01/2017-12-31",
               "time": "12:00",
               "format": "grib"
           },
           "dowload.grib")
