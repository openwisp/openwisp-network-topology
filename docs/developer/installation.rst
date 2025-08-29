Installation Instructions
=========================

.. include:: ../partials/developer-docs.rst

.. contents:: **Table of contents**:
    :depth: 2
    :local:

Installing for Development
--------------------------

Install the system dependencies:

.. code-block:: shell

    sudo apt install -y sqlite3 libsqlite3-dev
    # Install system dependencies for spatialite which is required
    # to run tests for openwisp-network-topology integrations with
    # openwisp-network-topology and openwisp-monitoring.
    sudo apt install libspatialite-dev libsqlite3-mod-spatialite

Fork and clone the forked repository:

.. code-block:: shell

    git clone git://github.com/<your_fork>/openwisp-network-topology

Navigate into the cloned repository:

.. code-block:: shell

    cd openwisp-network-topology/

Start InfluxDB and Redis using Docker (required by the test project to run
tests for :ref:`WiFi Mesh Integration
<OPENWISP_NETWORK_TOPOLOGY_WIFI_MESH_INTEGRATION>`):

.. code-block:: shell

    docker compose up -d influxdb redis

Setup and activate a virtual-environment (we'll be using `virtualenv
<https://pypi.org/project/virtualenv/>`_):

.. code-block:: shell

    python -m virtualenv env
    source env/bin/activate

Make sure that your base python packages are up to date before moving to
the next step:

.. code-block:: shell

    pip install -U pip wheel setuptools

Install development dependencies:

.. code-block:: shell

    pip install -e .
    pip install -r requirements-test.txt

Create database:

.. code-block:: shell

    cd tests/
    ./manage.py migrate
    ./manage.py createsuperuser

You can access the admin interface at ``http://127.0.0.1:8000/admin/``.

Run tests with:

.. code-block:: shell

    ./runtests

Run QA checks:

.. code-block:: shell

    ./run-qa-checks

Alternative Sources
-------------------

Pypi
~~~~

To install the latest Pypi:

.. code-block:: shell

    pip install openwisp-network-topology

Github
~~~~~~

To install the latest development version tarball via HTTPs:

.. code-block:: shell

    pip install https://github.com/openwisp/openwisp-network-topology/tarball/master

Alternatively you can use the git protocol:

.. code-block:: shell

    pip install -e git+git://github.com/openwisp/openwisp-network-topology#egg=openwisp_network-topology
