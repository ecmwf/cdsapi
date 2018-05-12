
Install
-------

Install via `pip` with::

    $ pip install cdsapi


Configure
---------

Get your API key from the CDS portal and write it into the configuration file::

    $ vim ~/.cdsapirc

Test
----

    $ python
    >>> import cdsapi
    >>> cds = cdsapi.Client()
    >>> cds.retrieve("insitu-glaciers-extent", {}, "target.data")
    ...
