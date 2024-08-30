Extending OpenWISP Network Topology
===================================

.. include:: ../partials/developer-docs.rst

One of the core values of the OpenWISP project is :ref:`Software
Reusability <values_software_reusability>`, for this reason
*openwisp-network-topology* provides a set of base classes which can be
imported, extended and reused to create derivative apps.

In order to implement your custom version of *openwisp-network-topology*,
you need to perform the steps described in this section.

When in doubt, the code in the `test project
<https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/>`_
and the `sample app
<https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_network_topology/>`_
will serve you as source of truth: just replicate and adapt that code to
get a basic derivative of *openwisp-network-topology* working.

.. important::

    If you plan on using a customized version of this module, we suggest
    to start with it since the beginning, because migrating your data from
    the default module to your extended version may be time consuming.

.. contents:: **Table of Contents**:
    :depth: 2
    :local:

1. Initialize your Custom Module
--------------------------------

The first thing you need to do is to create a new django app which will
contain your custom version of *openwisp-network-topology*.

A django app is nothing more than a `python package
<https://docs.python.org/3/tutorial/modules.html#packages>`_ (a directory
of python scripts), in the following examples we'll call this django app
``sample_network_topology``, but you can name it how you want:

.. code-block::

    django-admin startapp sample_network_topology

If you use the integration with openwisp-controller, you may want to
extend also the integration app if you need:

.. code-block::

    django-admin startapp sample_integration_device

Keep in mind that the command mentioned above must be called from a
directory which is available in your `PYTHON_PATH
<https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH>`_ so that
you can then import the result into your project.

Now you need to add ``sample_network_topology`` to ``INSTALLED_APPS`` in
your ``settings.py``, ensuring also that ``openwisp_network_topology`` has
been removed:

.. code-block:: python

    INSTALLED_APPS = [
        # ... other apps ...
        "openwisp_utils.admin_theme",
        # all-auth
        "django.contrib.sites",
        "openwisp_users.accounts",
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
        # (optional) openwisp_controller - required only if you are using the integration app
        "openwisp_controller.pki",
        "openwisp_controller.config",
        "reversion",
        "sortedm2m",
        # network topology
        # 'sample_network_topology' <-- uncomment and replace with your app-name here
        # (optional) required only if you need to extend the integration app
        # 'sample_integration_device' <-- uncomment and replace with your integration-app-name here
        "openwisp_users",
        # admin
        "django.contrib.admin",
        # rest framework
        "rest_framework",
    ]

For more information about how to work with django projects and django
apps, please refer to the `django documentation
<https://docs.djangoproject.com/en/4.2/intro/tutorial01/>`_.

2. Install ``openwisp-network-topology``
----------------------------------------

Install (and add to the requirement of your project)
openwisp-network-topology:

.. code-block::

    pip install openwisp-network-topology

3. Add ``EXTENDED_APPS``
------------------------

Add the following to your ``settings.py``:

.. code-block:: python

    EXTENDED_APPS = ("openwisp_network_topology",)

4. Add ``openwisp_utils.staticfiles.DependencyFinder``
------------------------------------------------------

Add ``openwisp_utils.staticfiles.DependencyFinder`` to
``STATICFILES_FINDERS`` in your ``settings.py``:

.. code-block:: python

    STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        "openwisp_utils.staticfiles.DependencyFinder",
    ]

5. Add ``openwisp_utils.loaders.DependencyLoader``
--------------------------------------------------

Add ``openwisp_utils.loaders.DependencyLoader`` to ``TEMPLATES`` in your
``settings.py``:

.. code-block:: python

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "OPTIONS": {
                "loaders": [
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                    "openwisp_utils.loaders.DependencyLoader",
                ],
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        }
    ]

6. Inherit the AppConfig Class
------------------------------

Please refer to the following files in the sample app of the test project:

- `sample_network_topology/__init__.py
  <https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_network_topology/__init__.py>`_.
- `sample_network_topology/apps.py
  <https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_network_topology/apps.py>`_.

For the integration with openwisp-controller, see:

- `sample_integration_device/__init__.py
  <https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_integration_device/__init__.py>`_.
- `sample_integration_device/apps.py
  <https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_integration_device/apps.py>`_.

You have to replicate and adapt that code in your project.

For more information regarding the concept of ``AppConfig`` please refer
to the `"Applications" section in the django documentation
<https://docs.djangoproject.com/en/4.2/ref/applications/>`_.

7. Create your Custom Models
----------------------------

Please refer to `sample_app models file
<https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_network_topology/models.py>`_
use in the test project.

You have to replicate and adapt that code in your project.

.. note::

    If you have questions about using, extending, or developing models,
    refer to the `"Models" section of the Django documentation
    <https://docs.djangoproject.com/en/4.2/topics/db/models/>`_.

8. Add Swapper Configurations
-----------------------------

Once you have created the models, add the following to your
``settings.py``:

.. code-block:: python

    # Setting models for swapper module
    TOPOLOGY_LINK_MODEL = "sample_network_topology.Link"
    TOPOLOGY_NODE_MODEL = "sample_network_topology.Node"
    TOPOLOGY_SNAPSHOT_MODEL = "sample_network_topology.Snapshot"
    TOPOLOGY_TOPOLOGY_MODEL = "sample_network_topology.Topology"
    # if you use the integration with OpenWISP Controller and/or OpenWISP Monitoring
    TOPOLOGY_DEVICE_DEVICENODE_MODEL = "sample_integration_device.DeviceNode"
    TOPOLOGY_DEVICE_WIFIMESH_MODEL = "sample_integration_device.WifiMesh"

Substitute ``sample_network_topology`` with the name you chose in step 1.

9. Create Database Migrations
-----------------------------

Create and apply database migrations:

.. code-block::

    ./manage.py makemigrations
    ./manage.py migrate

For more information, refer to the `"Migrations" section in the django
documentation
<https://docs.djangoproject.com/en/4.2/topics/migrations/>`_.

10. Create the Admin
--------------------

Refer to the `admin.py file of the sample app
<https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_network_topology/admin.py>`_.

To introduce changes to the admin, you can do it in two main ways which
are described below.

.. note::

    For more information regarding how the django admin works, or how it
    can be customized, please refer to `"The django admin site" section in
    the django documentation
    <https://docs.djangoproject.com/en/4.2/ref/contrib/admin/>`_.

1. Monkey Patching
~~~~~~~~~~~~~~~~~~

If the changes you need to add are relatively small, you can resort to
monkey patching.

For example:

.. code-block:: python

    from openwisp_network_topology.admin import (
        TopologyAdmin,
        LinkAdmin,
        NodeAdmin,
    )

    # TopologyAdmin.list_display.insert(1, 'my_custom_field') <-- your custom change example
    # LinkAdmin.list_display.insert(1, 'my_custom_field') <-- your custom change example
    # NodeAdmin.list_display.insert(1, 'my_custom_field') <-- your custom change example

2. Inheriting Admin Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to introduce significant changes and/or you don't want to
resort to monkey patching, you can proceed as follows:

.. code-block:: python

    from django.contrib import admin
    from swapper import load_model

    from openwisp_network_topology.admin import (
        TopologyAdmin as BaseTopologyAdmin,
        LinkAdmin as BaseLinkAdmin,
        NodeAdmin as BaseNodeAdmin,
    )

    Node = load_model("topology", "Node")
    Link = load_model("topology", "Link")
    Topology = load_model("topology", "Topology")

    admin.site.unregister(Topology)
    admin.site.unregister(Link)
    admin.site.unregister(Node)


    @admin.register(Topology, TopologyAdmin)
    class TopologyAdmin(BaseTopologyAdmin):
        # add your changes here
        pass


    @admin.register(Link, LinkAdmin)
    class LinkAdmin(BaseLinkAdmin):
        # add your changes here
        pass


    @admin.register(Node, NodeAdmin)
    class NodeAdmin(BaseNodeAdmin):
        # add your changes here
        pass

11. Create Root URL Configuration
---------------------------------

The following can be used to register all the URLs in your
    ``urls.py``.

Please read and replicate according to your project needs:

.. code-block:: python

    # If you've extended visualizer views (discussed below).
    # Import visualizer views & function to add it.
    # from openwisp_network_topology.utils import get_visualizer_urls
    # from .sample_network_topology.visualizer import views

    urlpatterns = [
        # If you've extended visualizer views (discussed below).
        # Add visualizer views in urls.py
        # path('topology/', include(get_visualizer_urls(views))),
        path("", include("openwisp_network_topology.urls")),
        path("admin/", admin.site.urls),
    ]

For more information about URL configuration in django, please refer to
the `"URL dispatcher" section in the django documentation
<https://docs.djangoproject.com/en/4.2/topics/http/urls/>`_.

12. Setup API URLs
------------------

You need to create a file ``api/urls.py`` (the name & path of the file
must match) inside your app, which contains the following:

.. code-block:: python

    from openwisp_network_topology.api import views

    # When you want to modify views, please change views location
    # from . import views
    from openwisp_network_topology.utils import get_api_urls

    urlpatterns = get_api_urls(views)

13. Extending Management Commands
---------------------------------

To extend the management commands, create
`sample_network_topology/management/commands` directory and two files in
it:

- `save_snapshot.py
  <https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_network_topology/management/commands/save_snapshot.py>`_
- `update_topology.py
  <https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_network_topology/management/commands/update_topology.py>`_

14. Import the Automated Tests
------------------------------

When developing a custom application based on this module, it's a good
idea to import and run the base tests too, so that you can be sure the
changes you're introducing are not breaking some of the existing features
of *openwisp-network-topology*.

Refer to the `tests.py file of the sample app
<https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_network_topology/tests.py>`_.

In case you need to add breaking changes, you can overwrite the tests
defined in the base classes to test your own behavior.

For testing you also need to extend the fixtures, you can copy the file
``openwisp_network_topology/fixtures/test_users.json`` in your sample
app's ``fixtures/`` directory.

Now, you can then run tests with:

.. code-block::

    # the --parallel flag is optional
    ./manage.py test --parallel sample_network_topology

Substitute ``sample_network_topology`` with the name you chose in step 1.

For more information about automated tests in django, please refer to
`"Testing in Django"
<https://docs.djangoproject.com/en/4.2/topics/testing/>`_.

Other Base Classes that can be Inherited and Extended
-----------------------------------------------------

The following steps are not required and are intended for more advanced
customization.

1. Extending API Views
~~~~~~~~~~~~~~~~~~~~~~

Extending the views is only required when you want to make changes in the
behavior of the API. Please refer to `sample_network_topology/api/views.py
<https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_network_topology/api/views.py>`_
and replicate it in your application.

If you extend these views, remember to use these views in the
``api/urls.py``.

2. Extending the Visualizer Views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to API views, visualizer views are only required to be extended
when you want to make changes in the Visualizer. Please refer to
`sample_network_topology/visualizer/views.py
<https://github.com/openwisp/openwisp-network-topology/tree/master/tests/openwisp2/sample_network_topology/visualizer/views.py>`_
and replicate it in your application.

If you extend these views, remember to use these views in the ``urls.py``.
