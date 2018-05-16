
.. highlight:: console

How to develop
--------------

Install the package following README.rst and then install development dependencies::

    $ pip install -U -r tests/requirements-dev.txt

Unit tests can be run with `pytest <https://pytest.org>`_ with::

    $ pytest -v --flakes --cov=cdsapi --cov-report=html --cache-clear

Coverage can be checked opening in a browser the file ``htmlcov/index.html`` for example with::

    $ open htmlcov/index.html

Code quality control checks can be run with::

    $ pytest -v --pep8 --mccabe

The complete python versions tests are run via `tox <https://tox.readthedocs.io>`_ with::

    $ tox

Please ensure the coverage at least stays the same before you submit a pull request.


Dependency management
---------------------

Update the `requirements-tests.txt` file with versions with::

    pip-compile -U -o tests/requirements-tests.txt setup.py tests/requirements-tests.in  # -U is optional


Release procedure
-----------------

Quality check release::

    $ git status
    $ check-manifest
    $ tox

Release with zest.releaser::

    $ prerelease
    $ release
    $ postrelease
