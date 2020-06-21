import logging

from django.conf import settings

# 'pre_django_setup' is supposed to be a logger
# that can work before registered Apps are
# ready in django.setup() process.
logger = logging.getLogger('pre_django_setup')


def get_settings_value(option, default):
    outdated_option_used = False
    if hasattr(settings, f'NETJSONGRAPH_{option}'):
        outdated_option_used = 'NETJSONGRAPH'
    elif hasattr(settings, f'TOPOLOGY_{option}'):
        outdated_option_used = 'TOPOLOGY'
    if outdated_option_used:
        logger.warn(
            f'{outdated_option_used}_{option} setting is deprecated. It will be removed '
            f'in the future, please use OPENWISP_NETWORK_TOPOLOGY_{option} instead.'
        )
        return getattr(settings, f'{outdated_option_used}_{option}')
    return getattr(settings, f'OPENWISP_NETWORK_TOPOLOGY_{option}', default)


DEFAULT_PARSERS = [
    ('netdiff.OlsrParser', 'OLSRd (txtinfo/jsoninfo)'),
    ('netdiff.BatmanParser', 'batman-advanced (jsondoc/txtinfo)'),
    ('netdiff.BmxParser', 'BMX6 (q6m)'),
    ('netdiff.NetJsonParser', 'NetJSON NetworkGraph'),
    ('netdiff.CnmlParser', 'CNML 1.0'),
    ('netdiff.OpenvpnParser', 'OpenVPN'),
]

PARSERS = DEFAULT_PARSERS + get_settings_value('PARSERS', [])
SIGNALS = get_settings_value('SIGNALS', None)
TIMEOUT = get_settings_value('TIMEOUT', 8)
LINK_EXPIRATION = get_settings_value('LINK_EXPIRATION', 60)
NODE_EXPIRATION = get_settings_value('NODE_EXPIRATION', False)
VISUALIZER_CSS = get_settings_value('VISUALIZER_CSS', 'netjsongraph/css/style.css')
TOPOLOGY_API_URLCONF = get_settings_value('API_URLCONF', None)
TOPOLOGY_API_BASEURL = get_settings_value('API_BASEURL', None)
