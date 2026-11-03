#!/usr/bin/env python

# (C) Copyright 2018 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

# Route all client traffic through a proxy by passing a custom requests.Session.

import requests

import cdsapi

PROXY = "http://user:pass@proxy.example.com:3128"

session = requests.Session()
session.proxies = {"http": PROXY, "https": PROXY}

c = cdsapi.Client(session=session)

c.retrieve(
    "reanalysis-era5-pressure-levels",
    {
        "product_type": ["reanalysis"],
        "variable": ["geopotential"],
        "year": ["2024"],
        "month": ["03"],
        "day": ["01"],
        "time": ["13:00"],
        "pressure_level": ["1000"],
        "data_format": "grib",
    },
    "download.grib",
)
