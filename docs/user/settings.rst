Settings
========

.. include:: /partials/settings-note.rst

``OPENWISP_NETWORK_TOPOLOGY_PARSERS``
-------------------------------------

============ ========
**type**:    ``list``
**default**: ``[]``
============ ========

Additional custom `netdiff parsers
<https://github.com/openwisp/netdiff#parsers>`_.

``OPENWISP_NETWORK_TOPOLOGY_SIGNALS``
-------------------------------------

============ ========
**type**:    ``str``
**default**: ``None``
============ ========

String representing Python module to import on initialization.

Useful for loading Django signals or to define custom behavior.

``OPENWISP_NETWORK_TOPOLOGY_TIMEOUT``
-------------------------------------

============ =======
**type**:    ``int``
**default**: ``8``
============ =======

Timeout when fetching topology URLs.

``OPENWISP_NETWORK_TOPOLOGY_LINK_EXPIRATION``
---------------------------------------------

============ =======
**type**:    ``int``
**default**: ``60``
============ =======

If a link is down for more days than this number, it will be deleted by
the ``update_topology`` management command.

Setting this to ``False`` will disable this feature.

``OPENWISP_NETWORK_TOPOLOGY_NODE_EXPIRATION``
---------------------------------------------

============ =========
**type**:    ``int``
**default**: ``False``
============ =========

If a node has not been modified since the days specified and if it has no
links, it will be deleted by the ``update_topology`` management command.
This depends on ``OPENWISP_NETWORK_TOPOLOGY_LINK_EXPIRATION`` being
enabled. Replace ``False`` with an integer to enable the feature.

``OPENWISP_NETWORK_TOPOLOGY_VISUALIZER_CSS``
--------------------------------------------

============ ==============================
**type**:    ``str``
**default**: ``netjsongraph/css/style.css``
============ ==============================

Path of the visualizer css file. Allows customization of css according to
user's preferences.

``OPENWISP_NETWORK_TOPOLOGY_API_URLCONF``
-----------------------------------------

============ ==========
**type**:    ``string``
**default**: ``None``
============ ==========

Use the ``urlconf`` option to change receive API URL to point to another
module, example, ``myapp.urls``.

``OPENWISP_NETWORK_TOPOLOGY_API_BASEURL``
-----------------------------------------

============ ==========
**type**:    ``string``
**default**: ``None``
============ ==========

If you have a separate instance of the OpenWISP Network Topology API on a
different domain, you can use this option to change the base of the URL,
this will enable you to point all the API URLs to your API server's
domain, example value: ``https://api.myservice.com``.

``OPENWISP_NETWORK_TOPOLOGY_API_AUTH_REQUIRED``
-----------------------------------------------

============ ===========
**type**:    ``boolean``
**default**: ``True``
============ ===========

When enabled, the API :ref:`endpoints <network_topology_rest_endpoints>`
will only allow authenticated users who have the necessary permissions to
access the objects which belong to the organizations the user manages.

.. _openwisp_network_topology_wifi_mesh_integration:

``OPENWISP_NETWORK_TOPOLOGY_WIFI_MESH_INTEGRATION``
---------------------------------------------------

============ ===========
**type**:    ``boolean``
**default**: ``False``
============ ===========

When enabled, network topology objects will be automatically created and
updated based on the WiFi mesh interfaces peer information supplied by the
monitoring agent.

.. note::

    The network topology objects are created using the device monitoring
    data collected by OpenWISP Monitoring. Thus, it requires
    :doc:`integration with OpenWISP Controller and OpenWISP Monitoring
    <integrations>` to be enabled in the Django project.
