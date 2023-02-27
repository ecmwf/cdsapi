import json
import sys

import cdsapi

with open("/input/request.json") as req:
    request = json.load(req)

cds = cdsapi.Client(request.get("url"), request.get("uuid") + ":" + request.get("key"))

cds.retrieve(
    request.get("variable"),
    request.get("options"),
    "/output/" + request.get("filename"),
)
