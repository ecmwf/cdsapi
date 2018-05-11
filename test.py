#!/usr/bin/env python

import cdsapi

c = cdsapi.Client()

#c.get_resource("insitu-glaciers-extent", {})

c.get_resource("insitu-glaciers-elevation-mass", { "variable": "elevation_change", "format": "tgz" } 
, "data.tgz")
