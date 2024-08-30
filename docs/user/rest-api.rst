Rest API
========

.. contents:: **Table of contents**:
    :depth: 1
    :local:

.. _network_topology_live_documentation:

Live Documentation
------------------

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-network-topology/docs/docs/api-doc.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-network-topology/docs/docs/api-doc.png
    :align: center

A general live API documentation (following the OpenAPI specification) at
``/api/v1/docs/``.

.. _network_topology_browsable_web_interface:

Browsable Web Interface
-----------------------

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-network-topology/docs/docs/api-ui.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-network-topology/docs/docs/api-ui.png
    :align: center

Additionally, opening any of the endpoints :ref:`listed below
<network_topology_rest_endpoints>` directly in the browser will show the
`browsable API interface of Django-REST-Framework
<https://www.django-rest-framework.org/topics/browsable-api/>`_, which
makes it even easier to find out the details of each endpoint.

.. _network_topology_rest_endpoints:

List of Endpoints
-----------------

Since the detailed explanation is contained in the
:ref:`network_topology_live_documentation` and in the
:ref:`network_topology_browsable_web_interface` of each point, here we'll
provide just a list of the available endpoints, for further information
please open the URL of the endpoint in your browser.

List Topologies
~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/network-topology/topology/

Available filters:

- ``strategy``: Filter topologies based on their strategy (``fetch`` or
  ``receive``). E.g. ``?strategy=<topology_strategy>``.
- ``parser``: Filter topologies based on their parser. E.g.
  ``?parser=<topology_parsers>``.
- ``organization``: Filter topologies based on their organization. E.g.
  ``?organization=<topology_organization_id>``.
- ``organization_slug``: Filter topologies based on their organization
  slug. E.g. ``?organization_slug=<topology_organization_slug>``.

You can use multiple filters in one request, e.g.:

.. code-block:: text

    /api/v1/network-topology/topology/?organization=371791ec-e3fe-4c9a-8972-3e8b882416f6&strategy=fetch

.. note::

    By default, ``/api/v1/network-topology/topology/`` does not include
    unpublished topologies. If you want to include unpublished topologies
    in the response, use ``?include_unpublished=true`` filter as
    following:

    .. code-block:: text

        GET /api/v1/network-topology/topology/?include_unpublished=true

Create Topology
~~~~~~~~~~~~~~~

.. code-block:: text

    POST /api/v1/network-topology/topology/

Detail of a Topology
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/network-topology/topology/{id}/

.. note::

    By default, ``/api/v1/network-topology/topology/{id}/`` will return
    ``HTTP 404 Not Found`` for unpublished topologies. If you want to
    retrieve an unpublished topology, use ``?include_unpublished=true``
    filter as following:

.. code-block:: text

    GET /api/v1/network-topology/topology/{id}/?include_unpublished=true

Change Topology Detail
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    PUT /api/v1/network-topology/topology/{id}/

Patch Topology Detail
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    PATCH /api/v1/network-topology/topology/{id}/

Delete Topology
~~~~~~~~~~~~~~~

.. code-block:: text

    DELETE /api/v1/network-topology/topology/{id}/

View Topology History
~~~~~~~~~~~~~~~~~~~~~

This endpoint is used to go back in time to view previous topology
snapshots. For it to work, snapshots need to be saved periodically as
described in :ref:`save_snapshot <network_topology_save_snapshot>` section
above.

For example, we could use the endpoint to view the snapshot of a topology
saved on ``2020-08-08`` as follows.

.. code-block:: text

    GET /api/v1/network-topology/topology/{id}/history/?date=2020-08-08

Send Topology Data
~~~~~~~~~~~~~~~~~~

.. code-block:: text

    POST /api/v1/network-topology/topology/{id}/receive/

List Links
~~~~~~~~~~

.. code-block:: text

    GET /api/v1/network-topology/link/

Available filters:

- ``topology``: Filter links belonging to a topology. E.g.
  ``?topology=<topology_id>``.
- ``organization``: Filter links belonging to an organization. E.g.
  ``?organization=<organization_id>``.
- ``organization_slug``: Filter links based on their organization slug.
  E.g. ``?organization_slug=<organization_slug>``.
- ``status``: Filter links based on their status (``up`` or ``down``).
  E.g. ``?status=<link_status>``.

You can use multiple filters in one request, e.g.:

.. code-block:: text

    /api/v1/network-topology/link/?status=down&topology=7fce01bd-29c0-48b1-8fce-0508f2d75d36

Create Link
~~~~~~~~~~~

.. code-block:: text

    POST /api/v1/network-topology/link/

Get Link Detail
~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/network-topology/link/{id}/

Change Link Detail
~~~~~~~~~~~~~~~~~~

.. code-block:: text

    PUT /api/v1/network-topology/link/{id}/

Patch Link Detail
~~~~~~~~~~~~~~~~~

.. code-block:: text

    PATCH /api/v1/network-topology/link/{id}/

Delete Link
~~~~~~~~~~~

.. code-block:: text

    DELETE /api/v1/network-topology/link/{id}/

List Nodes
~~~~~~~~~~

.. code-block:: text

    GET /api/v1/network-topology/node/

Available filters:

- ``topology``: Filter nodes belonging to a topology. E.g.
  ``?topology=<topology_id>``.
- ``organization``: Filter nodes belonging to an organization. E.g.
  ``?organization=<organization_id>``.
- ``organization_slug``: Filter nodes based on their organization slug.
  E.g. ``?organization_slug=<organization_slug>``.

You can use multiple filters in one request, e.g.:

.. code-block:: text

    /api/v1/network-topology/node/?organization=371791ec-e3fe-4c9a-8972-3e8b882416f6&topology=7fce01bd-29c0-48b1-8fce-0508f2d75d36

Create Node
~~~~~~~~~~~

.. code-block:: text

    POST /api/v1/network-topology/node/

Get Node Detail
~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/network-topology/node/{id}/

Change Node Detail
~~~~~~~~~~~~~~~~~~

.. code-block:: text

    PUT /api/v1/network-topology/node/{id}/

Patch Node Detail
~~~~~~~~~~~~~~~~~

.. code-block:: text

    PATCH /api/v1/network-topology/node/{id}/

Delete Node
~~~~~~~~~~~

.. code-block:: text

    DELETE /api/v1/network-topology/node/{id}/
