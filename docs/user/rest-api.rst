Rest API
--------

Live documentation
^^^^^^^^^^^^^^^^^^

.. image:: https://github.com/openwisp/openwisp-network-topology/raw/docs/docs/api-doc.png

A general live API documentation (following the OpenAPI specification) at ``/api/v1/docs/``.

Browsable web interface
^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://github.com/openwisp/openwisp-network-topology/raw/docs/docs/api-ui.png

Additionally, opening any of the endpoints `listed below <#list-of-endpoints>`_
directly in the browser will show the `browsable API interface of Django-REST-Framework
<https://www.django-rest-framework.org/topics/browsable-api/>`_,
which makes it even easier to find out the details of each endpoint.

List of endpoints
^^^^^^^^^^^^^^^^^

Since the detailed explanation is contained in the `Live documentation <#live-documentation>`_
and in the `Browsable web page <#browsable-web-interface>`_ of each point,
here we'll provide just a list of the available endpoints,
for further information please open the URL of the endpoint in your browser.

List topologies
###############

.. code-block:: text

    GET /api/v1/network-topology/topology/

Available filters:

- ``strategy``: Filter topologies based on their strategy (``fetch`` or ``receive``).
  E.g. ``?strategy=<topology_strategy>``.
- ``parser``: Filter topologies based on their parser.
  E.g. ``?parser=<topology_parsers>``.
- ``organization``: Filter topologies based on their organization.
  E.g. ``?organization=<topology_organization_id>``.
- ``organization_slug``: Filter topologies based on their organization slug.
  E.g. ``?organization_slug=<topology_organization_slug>``.

You can use multiple filters in one request, e.g.:

.. code-block:: text

    /api/v1/network-topology/topology/?organization=371791ec-e3fe-4c9a-8972-3e8b882416f6&strategy=fetch

**Note**: By default, ``/api/v1/network-topology/topology/`` does not include
unpublished topologies. If you want to include unpublished topologies in the
response, use ``?include_unpublished=true`` filter as following:

.. code-block:: text

    GET /api/v1/network-topology/topology/?include_unpublished=true

Create topology
###############

.. code-block:: text

    POST /api/v1/network-topology/topology/

Detail of a topology
####################

.. code-block:: text

    GET /api/v1/network-topology/topology/{id}/

**Note**: By default, ``/api/v1/network-topology/topology/{id}/`` will return
``HTTP 404 Not Found`` for unpublished topologies. If you want to retrieve an
unpublished topology, use ``?include_unpublished=true`` filter as following:

.. code-block:: text

    GET /api/v1/network-topology/topology/{id}/?include_unpublished=true

Change topolgy detail
#####################

.. code-block:: text

    PUT /api/v1/network-topology/topology/{id}/

Patch topology detail
#####################

.. code-block:: text

    PATCH /api/v1/network-topology/topology/{id}/

Delete topology
###############

.. code-block:: text

    DELETE /api/v1/network-topology/topology/{id}/

View topology history
#####################

This endpoint is used to go back in time to view previous topology snapshots.
For it to work, snapshots need to be saved periodically as described in
`save_snapshot <#save-snapshot>`_ section above.

For example, we could use the endpoint to view the snapshot of a topology
saved on ``2020-08-08`` as follows.

.. code-block:: text

    GET /api/v1/network-topology/topology/{id}/history/?date=2020-08-08

Send topology data
##################

.. code-block:: text

    POST /api/v1/network-topology/topology/{id}/receive/

List links
##########

.. code-block:: text

    GET /api/v1/network-topology/link/

Available filters:

- ``topology``: Filter links belonging to a topology.
  E.g. ``?topology=<topology_id>``.
- ``organization``: Filter links belonging to an organization.
  E.g. ``?organization=<organization_id>``.
- ``organization_slug``: Filter links based on their organization slug.
  E.g. ``?organization_slug=<organization_slug>``.
- ``status``: Filter links based on their status (``up`` or ``down``).
  E.g. ``?status=<link_status>``.

You can use multiple filters in one request, e.g.:

.. code-block:: text

    /api/v1/network-topology/link/?status=down&topology=7fce01bd-29c0-48b1-8fce-0508f2d75d36

Create link
###########

.. code-block:: text

    POST /api/v1/network-topology/link/

Get link detail
###############

.. code-block:: text

    GET /api/v1/network-topology/link/{id}/

Change link detail
##################

.. code-block:: text

    PUT /api/v1/network-topology/link/{id}/

Patch link detail
#################

.. code-block:: text

    PATCH /api/v1/network-topology/link/{id}/

Delete link
###########

.. code-block:: text

    DELETE /api/v1/network-topology/link/{id}/

List nodes
##########

.. code-block:: text

    GET /api/v1/network-topology/node/

Available filters:

- ``topology``: Filter nodes belonging to a topology.
  E.g. ``?topology=<topology_id>``.
- ``organization``: Filter nodes belonging to an organization.
  E.g. ``?organization=<organization_id>``.
- ``organization_slug``: Filter nodes based on their organization slug.
  E.g. ``?organization_slug=<organization_slug>``.

You can use multiple filters in one request, e.g.:

.. code-block:: text

    /api/v1/network-topology/node/?organization=371791ec-e3fe-4c9a-8972-3e8b882416f6&topology=7fce01bd-29c0-48b1-8fce-0508f2d75d36

Create node
###########

.. code-block:: text

    POST /api/v1/network-topology/node/

Get node detail
###############

.. code-block:: text

    GET /api/v1/network-topology/node/{id}/

Change node detail
##################

.. code-block:: text

    PUT /api/v1/network-topology/node/{id}/

Patch node detail
#################

.. code-block:: text

    PATCH /api/v1/network-topology/node/{id}/

Delete node
###########

.. code-block:: text

    DELETE /api/v1/network-topology/node/{id}/
