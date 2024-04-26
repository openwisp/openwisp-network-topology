OpenWISP Network Topology
=========================

OpenWISP Network Topology is a network topology collector and visualizer
web application and API, it allows to collect network topology data from different
networking software (dynamic mesh routing protocols, OpenVPN), store it,
visualize it, edit its details, it also provides hooks (a.k.a
`Django signals <https://docs.djangoproject.com/en/3.1/topics/signals/>`_)
to execute code when the status of a link changes.

When used in conjunction with
`OpenWISP Controller <https://github.com/openwisp/openwisp-controller>`_
and
`OpenWISP Monitoring <https://github.com/openwisp/openwisp-monitoring>`_,
it
`makes the monitoring system faster in detecting change to the network <#integration-with-openwisp-controller-and-openwisp-monitoring>`_.

**Available features**

* **network topology collector** supporting different formats:
    - NetJSON NetworkGraph
    - OLSR (jsoninfo/txtinfo)
    - batman-adv (jsondoc/txtinfo)
    - BMX6 (q6m)
    - CNML 1.0
    - OpenVPN
    - Wireguard
    - ZeroTier
    - additional formats can be added by
      `writing custom netdiff parsers <https://github.com/openwisp/netdiff#parsers>`_
* **network topology visualizer** based on
  `netjsongraph.js <https://github.com/openwisp/netjsongraph.js>`_
* `REST API <#rest-api>`_ that exposes data in
  `NetJSON <http://netjson.org>`__ *NetworkGraph* format
* **admin interface** that allows to easily manage, audit, visualize and
  debug topologies and their relative data (nodes, links)
* `RECEIVE network topology data <#receive-strategy>`_ from multiple nodes
* **topology history**: allows saving daily snapshots of each topology that
  can be viewed in the frontend
* **faster monitoring**: `integrates with OpenWISP Controller and OpenWISP Monitoring
  <#integration-with-openwisp-controller-and-openwisp-monitoring>`_
  for faster detection of critical events in the network

.. toctree::
   :maxdepth: 1

   ./user/quickstart.rst
   ./user/strategies.rst
   ./user/integration-with-controller-and-monitoring.rst
   ./user/settings.rst
   ./user/rest-api.rst
   ./developer/developer-docs.rst
