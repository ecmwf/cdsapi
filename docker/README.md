## Simple wrapper around cdsapi

cdsapi homepage : https://github.com/ecmwf/cdsapi

### How to use the dockerized version ?

1. Write a request in json file – don't forget the file format and name. Eg.

```js
{
  "url": "https://cds.climate.copernicus.eu/api/v2",
  "uuid": "<user id>",
  "key": "<user key>",
  "variable": "reanalysis-era5-pressure-levels",
  "options": {
    "variable": "temperature",
    "pressure_level": "1000",
    "product_type": "reanalysis",
    "date": "2017-12-01/2017-12-31",
    "time": "12:00",
    "format": "grib"
  },
  "filename":"test.grib"
}
```

2. Run the command

```sh 
docker run -it --rm \
  -v $(pwd)/request.json:/input/request.json \
  -v $(pwd)/.:/output \
  <YOUR REPO>/cdsretrieve 
```

Note : the file will be downloaded in the current folder, if not specified otherwise in the docker command. Inside the container, `/input` folder include the request and `/output` is target folder for the downloaded file.


