Changelog
=========

Verison 0.4.0 [2020-06-28]
--------------------------

- [refactoring] Merged code of django-netjsongraph in openwisp-network-topology
- [**breaking change**]: URLS at ``/api/`` moved to ``/api/v1/``
- [docs] Reordered & Improved docs
- [add] Requirement swapper~=1.1
- [docs] Added tutorial for extending openwisp-network-topology
- [feature] Upgrader script to upgrade from django-netjsongraph to openwisp-network-topology
- [change] Requirement netdiff~=0.8.0

Verison 0.3.2 [2020-06-02]
--------------------------

- [add] Support for openwisp-utils~=0.5.0
- [fix] swagger API fix for serializer

Verison 0.3.1 [2020-02-26]
--------------------------

- bumped min openwisp-utils 0.4.3
- bumped django-netjsongraph 0.6.1

Verison 0.3.0 [2020-02-06]
--------------------------

- Dropped support python 3.5 and below
- Dropped support django 2.1 and below
- Dropped support openwisp-users below 0.2.0
- Dropped support openwisp-utils 0.4.1 and below
- Dropped support django-netjsongraph below 0.6.0
- Added support for django 3.0

Verison 0.2.2 [2020-01-13]
--------------------------

- Updated dependencies
- Upgraded implementation of node addresses (via django-netjsongraph 0.5.0)

Verison 0.2.1 [2018-02-24]
--------------------------

- `fe9077c <https://github.com/openwisp/openwisp-network-topology/commit/fe9077c>`_:
   [models] Fixed related name of Link.target

Version 0.2.0 [2018-02-20]
--------------------------

- `cb7366 <https://github.com/openwisp/openwisp-network-topology/commit/cb7366>`_:
   [migrations] Added a migration file for link_status_changed and openvpn_parser
- `#22 <https://github.com/openwisp/openwisp-network-topology/pull/22>`_:
  Added support to django 2.0
- `d40032 <https://github.com/openwisp/openwisp-network-topology/commit/d40032>`_:
  [qa] Fixed variable name error
- `de45b6 <https://github.com/openwisp/openwisp-network-topology/commit/de45b6>`_:
  Upgraded code according to latest django-netjsongraph 0.4.0 changes
- `#17 <https://github.com/openwisp/openwisp-network-topology/pull/17>`_:
  Integrated topology history feature from django-netjsongraph

Version 0.1.2 [2017-07-22]
--------------------------

- `#13 <https://github.com/openwisp/openwisp-network-topology/issues/13>`_:
  Fixed the fetch and receive API bugs
- `#15 <https://github.com/openwisp/openwisp-network-topology/pull/15>`_:
  Imported admin tests from django-netjsongraph
- `#16 <https://github.com/openwisp/openwisp-network-topology/pull/16>`_:
  Added more tests by importing all from django-netjsongraph

Version 0.1.1 [2017-07-10]
--------------------------

- `95f8ade <https://github.com/openwisp/openwisp-network-topology/commit/95f8ade>`_: [admin] Moved submit_line.html to `openwisp-utils <https://github.com/openwisp/openwisp-utils>`_

Version 0.1 [2017-06-29]
------------------------

- Added multi-tenancy and integrated `django-netjsongraph <https://github.com/netjson/django-netjsongraph>`_
