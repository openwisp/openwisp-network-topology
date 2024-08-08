Integrations with other OpenWISP modules
========================================

If you use :doc:`OpenWISP Controller </controller/index>` or
:doc:`OpenWISP Monitoring </monitoring/index>` and you use OpenVPN,
Wireguard or ZeroTier for the management VPN, you can use the integration
available in ``openwisp_network_topology.integrations.device``.

This additional and optional module provides the following features:

- whenever the status of a link changes:

  - the management IP address of the related device is updated
    straightaway
  - if OpenWISP Monitoring is enabled, the device checks are triggered
    (e.g.: ping)

- if :doc:`OpenWISP Monitoring </monitoring/index>` is installed and
  enabled, the system can automatically create topology for the WiFi Mesh
  (802.11s) interfaces using the monitoring data provided by the agent.
  You can enable this by setting
  :ref:`OPENWISP_NETWORK_TOPOLOGY_WIFI_MESH_INTEGRATION
  <openwisp_network_topology_wifi_mesh_integration>` to ``True``.

This integration makes the whole system a lot faster in detecting
important events in the network.

.. include:: /partials/settings-note.rst

In order to use this module simply add
``openwisp_network_topology.integrations.device`` to ``INSTALLED_APPS`` in
the Django project settings, e.g.:

.. code-block:: python

    INSTALLED_APPS.append("openwisp_network_topology.integrations.device")

If you have enabled WiFI Mesh integration, you will also need to update
the ``CELERY_BEAT_SCHEDULE`` as follow:

.. code-block:: python

    CELERY_BEAT_SCHEDULE.update(
        {
            "create_mesh_topology": {
                # This task generates the mesh topology from monitoring data
                "task": "openwisp_network_topology.integrations.device.tasks.create_mesh_topology",
                # Execute this task every 5 minutes
                "schedule": timedelta(minutes=5),
                "args": (
                    # List of organization UUIDs. The mesh topology will be
                    # created only for devices belonging these organizations.
                    [
                        "4e002f97-eb01-4371-a4a8-857faa22fe5c",
                        "be88d4c4-599a-4ca2-a1c0-3839b4fdc315",
                    ],
                    # The task won't use monitoring data reported
                    # before this time (in seconds)
                    6 * 60,  # 6 minutes
                ),
            },
        }
    )

If you are enabling this integration on a preexisting system, use the
:ref:`create_device_nodes <network_topology_create_device_nodes>`
management command to create the relationship between devices and nodes.
