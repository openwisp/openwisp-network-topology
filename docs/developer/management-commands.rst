Management Commands
-------------------

``update_topology``
^^^^^^^^^^^^^^^^^^^

After topology URLs (URLs exposing the files that the topology of the network) have been
added in the admin, the ``update_topology`` management command can be used to collect data
and start playing with the network graph::

    ./manage.py update_topology

The management command accepts a ``--label`` argument that will be used to search in
topology labels, eg::

    ./manage.py update_topology --label mytopology

``save_snapshot``
^^^^^^^^^^^^^^^^^

The ``save_snapshot`` management command can be used to save the topology graph data which
could be used to view the network topology graph sometime in future::

    ./manage.py save_snapshot

The management command accepts a ``--label`` argument that will be used to search in
topology labels, eg::

    ./manage.py save_snapshot --label mytopology

``upgrade_from_django_netjsongraph``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are upgrading from django-netjsongraph to openwisp-network-topology, there
is an easy migration script that will import your topologies, users & groups to
openwisp-network-topology instance::

    ./manage.py upgrade_from_django_netjsongraph

The management command accepts an argument ``--backup``, that you can pass
to give the location of the backup files, by default it looks in the ``tests/``
directory, eg::

    ./manage.py upgrade_from_django_netjsongraph --backup /home/user/django_netjsongraph/

The management command accepts another argument ``--organization``, if you want to
import data to a specific organization, you can give its UUID for the same,
by default the data is added to the first found organization, eg::

    ./manage.py upgrade_from_django_netjsongraph --organization 900856da-c89a-412d-8fee-45a9c763ca0b

**Note**: you can follow the `tutorial to migrate database from django-netjsongraph <https://github.com/openwisp/django-netjsongraph/blob/master/README.rst>`_.

``create_device_nodes``
^^^^^^^^^^^^^^^^^^^^^^^

This management command can be used to create the initial ``DeviceNode`` relationships when the
`integration with OpenWISP Controller <#integration-with-openwisp-controller-and-openwisp-monitoring>`_
is enabled in a pre-existing system which already has some devices and topology objects in its database.

.. code-block:: shell

    ./manage.py create_device_nodes
