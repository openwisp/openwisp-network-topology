WebSocket API Reference
=======================

.. contents:: **Table of contents**:
    :depth: 2
    :local:

Overview
--------

The WebSocket API provides real-time topology updates.

All endpoints:

- Use JSON-encoded messages on the wire. The payload examples below are
  shown in JavaScript-style notation with inline comments for readability.
- Push real-time updates after the connection is established.
- Do not accept client messages: any data sent from the client is ignored.

Authentication and Authorization
--------------------------------

Authentication and authorization are controlled by
``OPENWISP_NETWORK_TOPOLOGY_API_AUTH_REQUIRED``, documented in
:doc:`settings`. The setting is enabled by default.

When authentication is required, WebSocket connections rely on the
standard Django session: connect from a browser context where the user is
logged in to OpenWISP so that the session cookie is sent during the
WebSocket handshake.

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
  - Has the ``topology.view_topology`` permission.

If ``OPENWISP_NETWORK_TOPOLOGY_API_AUTH_REQUIRED`` is set to ``False``,
any client can connect to an existing topology endpoint, including
unauthenticated users.

Client Message
++++++++++++++

The endpoint does not currently expose a request/response message for
retrieving the current state on demand. Messages are delivered when an
update event occurs.

.. warning::

    Any message sent by the client is ignored.

Real-time Updates
+++++++++++++++++

When a topology update is broadcast, the server sends a JSON message with
the following structure:

.. code-block:: javascript

    {
        "type": "broadcast_topology",     // Message type identifier
        "topology": {
            "...": "topology data"        // Current topology representation
        }
    }

The ``topology`` value contains the current topology representation
returned by the application, serialized as JSON.

A simplified example looks like this:

.. code-block:: javascript

    {
        "type": "broadcast_topology",
        "topology": {
            "type": "NetworkGraph",       // NetJSON graph type
            "protocol": "netjson.org",    // NetJSON protocol identifier
            "version": "1.0",             // NetJSON version
            "nodes": [],                  // Topology nodes
            "links": []                   // Topology links
        }
    }

Connected clients receive a new message whenever topology data changes.
Based on the current implementation and test coverage, updates are sent
when:

- Topology properties change.
- Nodes are created, updated, or deleted.
- Links are created, updated, or deleted.

Relationship with the REST API
------------------------------

The WebSocket endpoint complements the :doc:`rest-api` by providing live
topology updates to connected clients.

Use the REST API when you need to create, retrieve, update, delete, or
manually submit topology data. Use the WebSocket endpoint when you need to
observe changes to an existing topology in real time.
