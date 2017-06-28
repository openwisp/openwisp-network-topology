openwisp-network-topology
=========================

.. image:: https://travis-ci.org/openwisp/openwisp-network-topology.svg?branch=master
    :target: https://travis-ci.org/openwisp/openwisp-network-topology

.. image:: https://coveralls.io/repos/github/openwisp/openwisp-network-topology/badge.svg
    :target: https://coveralls.io/github/openwisp/openwisp-network-topology

.. image:: https://requires.io/github/openwisp/openwisp-network-topology/requirements.svg?branch=master
    :target: https://requires.io/github/openwisp/openwisp-network-topology/requirements/?branch=master
    :alt: Requirements Status

.. image:: https://badge.fury.io/py/openwisp-network-topology.svg
    :target: http://badge.fury.io/py/openwisp-network-topology

------------

OpenWISP 2 network topology module (built using Python and Django web-framework).

------------

.. contents:: **Table of Contents**:
   :backlinks: none
   :depth: 3

------------

Install stable version from pypi
--------------------------------

Install from pypi:

.. code-block:: shell

    pip install openwisp-network-topology

Install development version
---------------------------

Install tarball:

.. code-block:: shell

    pip install https://github.com/openwisp/openwisp-network-topology/tarball/master

Alternatively you can install via pip using git:

.. code-block:: shell

    pip install -e git+git://github.com/openwisp/openwisp-network-topology#egg=openwisp-network-topology

If you want to contribute, install your cloned fork:

.. code-block:: shell

    git clone git@github.com:<your_fork>/openwisp-network-topology.git
    cd openwisp-network-topology
    python setup.py develop

Setup (integrate in an existing django project)
-----------------------------------------------

``INSTALLED_APPS`` in ``settings.py`` should look like the following (order is important):

.. code-block:: python

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        # for customized openwisp admin theme
        'openwisp_utils.admin_theme',
        # all-auth
        'django.contrib.sites',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        # openwisp2 modules
        'openwisp_users',
        'openwisp_network_topology',
        # admin
        'django.contrib.admin',
    ]

Add ``openwisp_utils.staticfiles.DependencyFinder`` to ``STATICFILES_FINDERS`` in your settings.py

.. code-block:: python

    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'openwisp_utils.staticfiles.DependencyFinder',
    ]

Add ``openwisp_utils.loaders.DependencyLoader`` to ``TEMPLATES`` in your ``settings.py``

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'OPTIONS': {
                'loaders': [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'openwisp_utils.loaders.DependencyLoader',
                ],
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

Add the following settings to ``settings.py``

.. code-block:: python
    
    LOGIN_REDIRECT_URL = 'admin:index'
    ACCOUNT_LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL

Add the URLs to your main ``urls.py``:

.. code-block:: python

    from django.conf.urls import include, url
    from django.contrib import admin
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    
    from openwisp_network_topology import urls as urls


    urlpatterns = [
        url(r'^', include(urls)),
        url(r'^admin/', include(admin.site.urls)),
    ]
   
    urlpatterns += staticfiles_urlpatterns()

Then run:

.. code-block:: shell

    ./manage.py migrate

Installing for development
--------------------------

Install sqlite:

.. code-block:: shell

    sudo apt-get install sqlite3 libsqlite3-dev

Install your forked repo:

.. code-block:: shell

    git clone git://github.com/<your_fork>/openwisp-network-topology
    cd openwisp-network-topology/
    python setup.py develop

Install test requirements:

.. code-block:: shell

    pip install -r requirements-test.txt

Create database:

.. code-block:: shell

    cd tests/
    ./manage.py migrate
    ./manage.py createsuperuser

Set ``EMAIL_PORT`` in ``settings.py`` to a port number (eg: ``1025``):

.. code-block:: python

    EMAIL_PORT = '1025'

Launch development server and SMTP deubgging server:

.. code-block:: shell

    ./manage.py runserver
    # open another session and run
    python -m smtpd -n -c DebuggingServer localhost:1025

You can access the admin interface at http://127.0.0.1:8000/admin/.

Run tests with:

.. code-block:: shell

    ./runtests.py

Contributing
------------

1. Announce your intentions in the `OpenWISP Mailing List <https://groups.google.com/d/forum/openwisp>`_ and open relavant issues using the `issue tracker <https://github.com/openwisp/openwisp-network-topology/issues>`_
2. Fork this repo and install the project following the `instructions <https://github.com/openwisp/openwisp-network-topology#install-development-version>`_
3. Follow `PEP8, Style Guide for Python Code`_
4. Write code and corresponding tests
5. Ensure that all tests pass and the test coverage does not decrease
6. Document your changes
7. Send a pull request

.. _PEP8, Style Guide for Python Code: http://www.python.org/dev/peps/pep-0008/

Changelog
---------

See `CHANGES <https://github.com/openwisp/openwisp-network-topology/blob/master/CHANGES.rst>`_.

License
-------

See `LICENSE <https://github.com/openwisp/openwisp-network-topology/blob/master/LICENSE>`_.

Support
-------

See `OpenWISP Support Channels <http://openwisp.org/support.html>`_.
