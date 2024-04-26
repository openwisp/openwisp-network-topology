Installation instructions
-------------------------

Install stable version from pypi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install from pypi:

.. code-block:: shell

    pip install openwisp-network-topology

Install development version
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install tarball:

.. code-block:: shell

    pip install https://github.com/openwisp/openwisp-network-topology/tarball/master

Alternatively you can install via pip using git:

.. code-block:: shell

    pip install -e git+git://github.com/openwisp/openwisp-network-topology#egg=openwisp-network-topology

If you want to contribute, install your cloned fork:

.. code-block:: shell

    git clone git@github.com:<your_fork>/openwisp-network-topology.git
    cd openwisp-network-topology
    python setup.py develop

Installing for development
^^^^^^^^^^^^^^^^^^^^^^^^^^

Install sqlite:

.. code-block:: shell

    sudo apt install -y sqlite3 libsqlite3-dev
    # Install system dependencies for spatialite which is required
    # to run tests for openwisp-network-topology integrations with
    # openwisp-controller and openwisp-monitoring.
    sudo apt install libspatialite-dev libsqlite3-mod-spatialite

Install your forked repo:

.. code-block:: shell

    git clone git://github.com/<your_fork>/openwisp-network-topology
    cd openwisp-network-topology/
    python setup.py develop

Start InfluxDB and Redis using Docker
(required by the test project to run tests for
:ref:`WiFi Mesh Integration <OPENWISP_NETWORK_TOPOLOGY_WIFI_MESH_INTEGRATION>`):

.. code-block:: shell

    docker-compose up -d influxdb redis

Install test requirements:

.. code-block:: shell

    pip install -r requirements-test.txt

Create database:

.. code-block:: shell

    cd tests/
    ./manage.py migrate
    ./manage.py createsuperuser

You can access the admin interface at http://127.0.0.1:8000/admin/.

Run tests with:

.. code-block:: shell

    # Running tests without setting the "WIFI_MESH" environment
    # variable will not run tests for WiFi Mesh integration.
    # This is done to avoid slowing down the test suite by adding
    # dependencies which are only used by the integration.
    ./runtests.py
    # You can run the tests only for WiFi mesh integration using
    # the following command
    WIFI_MESH=1 ./runtests.py

Run qa tests:

.. code-block:: shell

    ./run-qa-checks
