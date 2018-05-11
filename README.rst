
Install
-------

Install via `pip` with::

    $ pip install cdsapi


Configure
---------

Get your API key from the CDS portal and write it into the configuration file::

    $ vim ~/.cdsapi

Test
----

    $ python
    >>> import cdsapi
    >>> cds = cdsapi.Client()
    >>> cds.get_resource("insitu-glaciers-extent", {})
    ...
