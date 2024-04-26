Settings
--------

``OPENWISP_NETWORK_TOPOLOGY_PARSERS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+-------------+
| **type**:    | ``list``    |
+--------------+-------------+
| **default**: | ``[]``      |
+--------------+-------------+

Additional custom `netdiff parsers <https://github.com/openwisp/netdiff#parsers>`_.

``OPENWISP_NETWORK_TOPOLOGY_SIGNALS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+-------------+
| **type**:    | ``str``     |
+--------------+-------------+
| **default**: | ``None``    |
+--------------+-------------+

String representing python module to import on initialization.

Useful for loading django signals or to define custom behaviour.

``OPENWISP_NETWORK_TOPOLOGY_TIMEOUT``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+-------------+
| **type**:    | ``int``     |
+--------------+-------------+
| **default**: | ``8``       |
+--------------+-------------+

Timeout when fetching topology URLs.

``OPENWISP_NETWORK_TOPOLOGY_LINK_EXPIRATION``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+-------------+
| **type**:    | ``int``     |
+--------------+-------------+
| **default**: | ``60``      |
+--------------+-------------+

If a link is down for more days than this number, it will be deleted by the
``update_topology`` management command.

Setting this to ``False`` will disable this feature.

``OPENWISP_NETWORK_TOPOLOGY_NODE_EXPIRATION``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+--------------------------------+
| **type**:    | ``int``                        |
+--------------+--------------------------------+
| **default**: | ``False``                      |
+--------------+--------------------------------+

If a node has not been modified since the days specified and if it has no links,
it will be deleted by the ``update_topology`` management command. This depends on
``OPENWISP_NETWORK_TOPOLOGY_LINK_EXPIRATION`` being enabled.
Replace ``False`` with an integer to enable the feature.

``OPENWISP_NETWORK_TOPOLOGY_VISUALIZER_CSS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+--------------------------------+
| **type**:    | ``str``                        |
+--------------+--------------------------------+
| **default**: | ``netjsongraph/css/style.css`` |
+--------------+--------------------------------+

Path of the visualizer css file. Allows customization of css according to user's
preferences.

``OPENWISP_NETWORK_TOPOLOGY_API_URLCONF``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+---------------+
| **type**:    |   ``string``  |
+--------------+---------------+
| **default**: |   ``None``    |
+--------------+---------------+

Use the ``urlconf`` option to change receive api url to point to
another module, example, ``myapp.urls``.

``OPENWISP_NETWORK_TOPOLOGY_API_BASEURL``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+---------------+
| **type**:    |   ``string``  |
+--------------+---------------+
| **default**: |   ``None``    |
+--------------+---------------+

If you have a seperate instance of openwisp-network-topology on a
different domain, you can use this option to change the base
of the url, this will enable you to point all the API urls to
your openwisp-network-topology API server's domain,
example value: ``https://mytopology.myapp.com``.

``OPENWISP_NETWORK_TOPOLOGY_API_AUTH_REQUIRED``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+---------------+
| **type**:    |   ``boolean`` |
+--------------+---------------+
| **default**: |   ``True``    |
+--------------+---------------+

When enabled, the API `endpoints <#list-of-endpoints>`_ will only allow authenticated users
who have the necessary permissions to access the objects which
belong to the organizations the user manages.

OPENWISP_NETWORK_TOPOLOGY_WIFI_MESH_INTEGRATION
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------+---------------+
| **type**:    |   ``boolean`` |
+--------------+---------------+
| **default**: |   ``False``   |
+--------------+---------------+

When enabled, network topology objects will be automatically created and
updated based on the WiFi mesh interfaces peer information supplied
by the monitoring agent.

**Note:** The network topology objects are created using the device monitoring data
collected by OpenWISP Monitoring. Thus, it requires
`integration with OpenWISP Controller and OpenWISP Monitoring
<#integration-with-openwisp-controller-and-openwisp-monitoring>`_ to be enabled
in the Django project.
