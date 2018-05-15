
Install
-------

Install via `pip` with::

    $ pip install cdsapi


Configure
---------

Get your UID and API key from the CDS portal at the address https://cds-toolbox-test.bopen.eu/user
and write it into the configuration file, so it looks like::

    $ cat ~/.cdsapirc
    url: https://cds-toolbox-test.bopen.eu/api/v2
    key: <UID>:<API key>
    verify: 0

Remember to agree to the Terms and Conditions of every dataset that you intend to download.


Test
----

Perform a small test retrieve of ERA5 data::

    $ python
    >>> import cdsapi
    >>> cds = cdsapi.Client()
    >>> cds.retrieve('reanalysis-era5-pressure-levels', {
               "variable": "temperature",
               "pressure_level": "1000",
               "product_type": "reanalysis",
               "date": "2017-12-01/2017-12-31",
               "time": "12:00",
               "format": "grib"
           }, 'download.grib')
    >>>
