#!/usr/bin/env python

import cdsapi
import logging


logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)

c = cdsapi.Client()

#c.get_resource("insitu-glaciers-extent", {})

c.get_resource("insitu-glaciers-elevation-mass", {"variable": "elevation_change", "format": "zip"}, "data.zip")
