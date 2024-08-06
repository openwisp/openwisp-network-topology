Topology Collection Strategies
==============================

There are mainly two ways of collecting topology information:

- **FETCH** strategy
- **RECEIVE** strategy

Each ``Topology`` instance has a ``strategy`` field which can be set to
the desired setting.

.. _network_topology_fetch_strategy:

FETCH Strategy
--------------

Topology data will be fetched from a URL.

When some links are not detected anymore they will be flagged as "down"
straightaway.

.. _network_topology_receive_strategy:

RECEIVE Strategy
----------------

Topology data is sent directly from one or more nodes of the network.

The collector waits to receive data in the payload of a POST HTTP request;
when such a request is received, a ``key`` parameter it's first checked
against the ``Topology`` key.

If the request is authorized the collector proceeds to update the
topology.

If the data is sent from one node only, it's highly advised to set the
``expiration_time`` of the ``Topology`` instance to ``0`` (seconds), this
way the system works just like in the **FETCH strategy**, with the only
difference that the data is sent by one node instead of fetched by the
collector.

If the data is sent from multiple nodes, you **SHOULD** set the
``expiration_time`` of the ``Topology`` instance to a value slightly
higher than the interval used by nodes to send the topology, this way
links will be flagged as "down" only if they haven't been detected for a
while. This mechanism allows to visualize the topology even if the network
has been split in several parts, the disadvantage is that it will take a
bit more time to detect links that go offline.
