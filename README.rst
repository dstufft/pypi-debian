PyPI Debian
===========

PyPI Debian is a simple redirector for PyPI which enables Debian's uscan to
easily detect versions from PyPI.


Usage
-----

Simply install pypi_debian and then using any wsgi server run the application
located at ``pypi_debian.wsgi:application``, for example with gunicorn:

.. code-block:: bash

    $ gunicorn pypi_debian.wsgi
