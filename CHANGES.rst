Changelog
=========

Version 1.2.0 [Unreleased]
--------------------------

Work in progress.

Version 1.1.1 [2024-11-26]
--------------------------

Bugfixes
~~~~~~~~

- Fixed websocket connection to use
  ``OPENWISP_NETWORK_TOPOLOGY_API_BASEURL``.
- Upgraded the ``netjsongraph.js`` library to include a patch for sending
  credentials in fetch requests.

Version 1.1.0 [2024-11-22]
--------------------------

Features
~~~~~~~~

- Added integration with `OpenWISP Monitoring to generate WiFi mesh
  network topology
  <https://openwisp.io/docs/stable/network-topology/user/integrations.html>`_.
- Added WireGuard topology parser and integration with OpenWISP Controller
- Added ZeroTier topology parser and integration with OpenWISP Controller
- Implemented real-time updates for topologies
- Added autocomplete support for filters in the admin interface
- Added filters to the REST API.

Changes
~~~~~~~

- Moved REST API topology collection database writes to a background
  worker
- Hid the "receive_url" field in ``TopologyAdmin`` when adding a topology

Dependencies
++++++++++++

- Bumped ``openwisp-users~=1.1.0``
- Bumped ``netdiff~=1.1.0``
- Bumped ``django-flat-json-widget~=0.3.0``
- Bumped ``openwisp-utils[celery]~=1.1.0``
- Added support for Django ``4.1.x`` and ``4.2.x``
- Added support for Python ``3.10``
- Dropped support for Python ``3.7``
- Dropped support for Django ``3.0.x`` and ``3.1.x``

Bugfixes
~~~~~~~~

- Fixed visualizer issues in both admin and non-admin interfaces
- Fixed changing status of link from admin page
- Resolved graph visualizer issue for unpublished topologies in admin
- User need to have required model permissions to perform admin actions

Version 1.0.0 [2022-05-06]
--------------------------

Features
~~~~~~~~

- Switched to new OpenWISP theme, registered the new menu items
- Added more REST API endpoint to manipulate details of Topology, Node and
  Link

Changes
~~~~~~~

Backward incompatible changes
+++++++++++++++++++++++++++++

- Changed URL prefix of REST API from to ``/api/v1/topology/``
  ``/api/v1/network-topology/`` for consistency with the other OpenWISP
  Modules
- Removed deprecated old receive topology API url; use the new URL:
  ``/api/v1/network-topology/topology/{id}/receive/``

Dependencies
++++++++++++

- Dropped support for Python 3.6
- Added support for Python 3.8 and Python 3.9
- Dropped support for Django 2.2
- Added support for Django 3.2 and 4.0
- Increased OpenWISP Users version to 1.0.0
- Removed redundant django-model-utils (it's defined in openwisp-utils)

Other changes
+++++++++++++

- Moved uuid field of topology admin after main fields
- Changed "View topology graph" button color
- Added the `openwisp-utils DjangoModelPermissions
  <https://github.com/openwisp/openwisp-users#djangomodelpermissions>`_
  class to API views
- Allow nodes, link and topologies to be shared among different
  organizations

Bugfixes
~~~~~~~~

- Ensured ``Link`` and ``Node`` belong to the same topology
- Removed use of custom ``has_permission()`` of old openwisp-utils
- Make sure migrations depend on swappable openwisp modules
- Load Organization model with swappable in tests

Version 0.5.1 [2020-11-25]
--------------------------

- [fix] Removed static() call from media assets
- [change] Increased `openwisp-users
  <https://github.com/openwisp/openwisp-users#openwisp-users>`__ version
  from 0.2.x to 0.5.x (which brings many interesting improvements to
  multi-tenancy, `see the change log of openwisp-users
  <https://github.com/openwisp/openwisp-users/blob/master/CHANGES.rst#version-050-2020-11-18>`_
  for more information)
- Increased `openwisp-utils
  <https://github.com/openwisp/openwisp-utils#openwisp-utils>`__ version
  to 0.7.x

Version 0.5.0 [2020-09-18]
--------------------------

Features
~~~~~~~~

- Added `integration with OpenWISP Controller and OpenWISP Monitoring
  <https://github.com/openwisp/openwisp-network-topology#integration-with-openwisp-controller-and-openwisp-monitoring>`_
- API: added `swagger API docs
  <https://github.com/openwisp/openwisp-network-topology/#rest-api>`_
- Admin: added UUID readonly field
- Added user defined properties in Node and Link

Changes
~~~~~~~

- **Backward incompatible**: API and visualizer views now require
  authentication by default. This can be changed through the new
  `OPENWISP_NETWORK_TOPOLOGY_API_AUTH_REQUIRED
  <https://github.com/openwisp/openwisp-network-topology#openwisp-network-topology-api-auth-required>`_
  setting
- Upgraded openvpn nodes to netdiff 0.9
- Automatically manage organization of Node and Link
- Changed API URL: /api/v1/receive/{id}/ ->
  /api/v1//topology/{id}/receive/ (old URL kept for backward
  compatibility)

Bugfixes
~~~~~~~~

- Fixed link status bug introduced in 0.4
- Fixed exceptions during update of data
- Do not save ``status_changed``, ``modified``, ``created`` in link
  properties
- Fixed Topology admin for users who do not have delete permission

Version 0.4.0 [2020-06-28]
--------------------------

- [refactoring] Merged code of django-netjsongraph in
  openwisp-network-topology
- [**breaking change**]: URLS at ``/api/`` moved to ``/api/v1/``
- [docs] Reordered & Improved docs
- [add] Requirement swapper~=1.1
- [docs] Added tutorial for extending openwisp-network-topology
- [feature] Upgrader script to upgrade from django-netjsongraph to
  openwisp-network-topology
- [change] Requirement netdiff~=0.8.0

Version 0.3.2 [2020-06-02]
--------------------------

- [add] Support for openwisp-utils~=0.5.0
- [fix] swagger API fix for serializer

Version 0.3.1 [2020-02-26]
--------------------------

- bumped min openwisp-utils 0.4.3
- bumped django-netjsongraph 0.6.1

Version 0.3.0 [2020-02-06]
--------------------------

- Dropped support python 3.5 and below
- Dropped support django 2.1 and below
- Dropped support openwisp-users below 0.2.0
- Dropped support openwisp-utils 0.4.1 and below
- Dropped support django-netjsongraph below 0.6.0
- Added support for django 3.0

Version 0.2.2 [2020-01-13]
--------------------------

- Updated dependencies
- Upgraded implementation of node addresses (via django-netjsongraph
  0.5.0)

Version 0.2.1 [2018-02-24]
--------------------------

- `fe9077c <https://github.com/openwisp/openwisp-network-topology/commit/fe9077c>`_:
      [models] Fixed related name of Link.target

Version 0.2.0 [2018-02-20]
--------------------------

- `cb7366 <https://github.com/openwisp/openwisp-network-topology/commit/cb7366>`_:
      [migrations] Added a migration file for link_status_changed and
      openvpn_parser
- `#22 <https://github.com/openwisp/openwisp-network-topology/pull/22>`_:
  Added support to django 2.0
- `d40032
  <https://github.com/openwisp/openwisp-network-topology/commit/d40032>`_:
  [qa] Fixed variable name error
- `de45b6
  <https://github.com/openwisp/openwisp-network-topology/commit/de45b6>`_:
  Upgraded code according to latest django-netjsongraph 0.4.0 changes
- `#17 <https://github.com/openwisp/openwisp-network-topology/pull/17>`_:
  Integrated topology history feature from django-netjsongraph

Version 0.1.2 [2017-07-22]
--------------------------

- `#13
  <https://github.com/openwisp/openwisp-network-topology/issues/13>`_:
  Fixed the fetch and receive API bugs
- `#15 <https://github.com/openwisp/openwisp-network-topology/pull/15>`_:
  Imported admin tests from django-netjsongraph
- `#16 <https://github.com/openwisp/openwisp-network-topology/pull/16>`_:
  Added more tests by importing all from django-netjsongraph

Version 0.1.1 [2017-07-10]
--------------------------

- `95f8ade
  <https://github.com/openwisp/openwisp-network-topology/commit/95f8ade>`_:
  [admin] Moved submit_line.html to `openwisp-utils
  <https://github.com/openwisp/openwisp-utils>`_

Version 0.1 [2017-06-29]
------------------------

- Added multi-tenancy and integrated `django-netjsongraph
  <https://github.com/netjson/django-netjsongraph>`_
