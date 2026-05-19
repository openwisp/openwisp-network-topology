WebSocket API Reference
=======================

.. contents:: **Table of contents**:
    :depth: 2
    :local:

Overview
--------

The WebSocket API provides real-time, push-based topology updates.

Current endpoint behavior:

- Use JSON-encoded messages on the wire.
- Push real-time updates after the connection is established.
- Do not currently define any client-to-server message contract.

Authentication and Authorization
--------------------------------

The WebSocket endpoint relies on the standard Django session. When
authentication is required, connect from a browser context where the user
is logged in so that the session cookie is sent during the WebSocket
handshake.

Authorization is controlled by
``OPENWISP_NETWORK_TOPOLOGY_API_AUTH_REQUIRED``, documented in
:doc:`settings`.

If the requested topology does not exist or the user is not authorized,
the connection is closed immediately.

Connection Endpoints
--------------------

1. Topology Updates
~~~~~~~~~~~~~~~~~~~

Connection URL:

::

    wss://<host>/ws/network-topology/topology/<topology_id>/

In local development or other non-TLS setups, the ``ws://`` scheme may be
used instead of ``wss://``.

Scope
+++++

Real-time updates for a single topology identified by ``<topology_id>``.

Authorization
+++++++++++++

When ``OPENWISP_NETWORK_TOPOLOGY_API_AUTH_REQUIRED`` is set to ``True``,
the connection is accepted only if the user is authorized to view the
requested topology.

A user is authorized if:

- The user is a superuser, OR
- The user:

  - Is authenticated,
  - Is an organization manager for the topology's organization,
  - Has the ``view_topology`` permission.

If ``OPENWISP_NETWORK_TOPOLOGY_API_AUTH_REQUIRED`` is set to ``False``,
any client can connect to an existing topology endpoint, including
unauthenticated users.

Real-time Updates
+++++++++++++++++

When a topology update is broadcast, the server sends a JSON message with
the following structure:

.. code-block:: javascript

    {
        "type": "broadcast_topology",
        "topology": {
            "...": "topology data"
        }
    }

The ``topology`` value contains the current topology representation
returned by the application, serialized as JSON.

A simplified example looks like this:

.. code-block:: javascript

    {
        "type": "broadcast_topology",
        "topology": {
            "type": "NetworkGraph",
            "protocol": "netjson.org",
            "version": "1.0",
            "nodes": [],
            "links": []
        }
    }

Connected clients receive a new message whenever topology data changes.
Based on the current implementation and test coverage, updates are sent
when:

- topology properties change
- nodes are created, updated, or deleted
- links are created, updated, or deleted

The connection does not currently expose a request/response message for
retrieving the current state on demand. Messages are delivered when an
update event occurs.

Relationship with the REST API
------------------------------

The WebSocket endpoint complements the :doc:`rest-api` by providing live
topology updates to connected clients.

Use the REST API when you need to create, retrieve, update, delete, or
manually submit topology data. Use the WebSocket endpoint when you need to
observe changes to an existing topology in real time.
