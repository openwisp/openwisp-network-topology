VERSION = (0, 1, 0, 'alpha')
__version__ = VERSION  # alias


def get_version():
    version = '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])
    if VERSION[3] != 'final':
        first_letter = VERSION[3][0:1]
        try:
            suffix = VERSION[4]
        except IndexError:
            suffix = 0
        version = '%s%s%s' % (version, first_letter, suffix)
    return version


# openwisp-network-topology extends and depends on these apps which
# cannot be listed in ``settings.INSTALLED_APPS``
# this variable is used by:
#     - openwisp_network_topology.staticfiles.DependencyFinder
#     - openwisp_network_topology.loaders.DependecyLoader
__dependencies__ = (
    'django_netjsongraph',
)

default_app_config = 'openwisp_network_topology.apps.OpenwispNetworkTopologyConfig'
