Network Topology: Features
==========================

OpenWISP Network Topology module offers robust features for managing,
visualizing, and monitoring network topologies. Key features include:

.. _network_topology_collectors:

- **network topology collector** supporting different formats:
      - NetJSON NetworkGraph
      - OLSR (jsoninfo/txtinfo)
      - batman-adv (jsondoc/txtinfo)
      - BMX6 (q6m)
      - CNML 1.0
      - OpenVPN
      - Wireguard
      - ZeroTier
      - additional formats can be added by `writing custom netdiff parsers
        <https://github.com/openwisp/netdiff#parsers>`_
- **network topology visualizer** based on `netjsongraph.js
  <https://github.com/openwisp/netjsongraph.js>`_
- :doc:`rest-api` that exposes data in `NetJSON <http://netjson.org>`__
  *NetworkGraph* format
- **admin interface** that allows to easily manage, audit, visualize and
  debug topologies and their relative data (nodes, links)
- :ref:`RECEIVE network topology data <network_topology_receive_strategy>`
  from multiple nodes
- **topology history**: allows saving daily snapshots of each topology
  that can be viewed in the frontend
- **faster monitoring**: :doc:`integrates with OpenWISP Controller and
  OpenWISP Monitoring <integrations>` for faster detection of critical
  events in the network
