#!/usr/bin/env python

import cdsapi
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')


c = cdsapi.Client()


c.retrieve("insitu-glaciers-elevation-mass",
           {"variable": "elevation_change", "format": "tgz"},
           "data.tgz")
