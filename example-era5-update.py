#!/usr/bin/env python

# (C) Copyright 2018 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import time
import cdsapi

c = cdsapi.Client(debug=True, wait_until_complete=False)

r = c.retrieve(
    "reanalysis-era5-single-levels",
    {
       "variable": "2t",
       "product_type": "reanalysis",
       "date": "2015-12-01",
       "time": "14:00",
       "format": "netcdf",
    },
)

sleep = 30
while True:
    r.update()
    reply = r.reply
    r.info("Request ID: %s, state: %s" % (reply['request_id'], reply['state']))

    if reply['state'] == 'completed':
        break
    elif reply['state'] in ('queued', 'running'):
        r.info("Request ID: %s, sleep: %s", reply['request_id'], sleep)
        time.sleep(sleep)
    elif reply['state'] in ('failed',):
        r.error("Message: %s", reply['error'].get('message'))
        r.error("Reason:  %s", reply['error'].get('reason'))
        for n in reply.get('error', {}).get('context', {}).get('traceback', '').split('\n'):
            if n.strip() == '':
                break
            r.error("  %s", n)
        raise Exception("%s. %s." % (reply['error'].get('message'), reply['error'].get('reason')))

r.download("test.nc")
