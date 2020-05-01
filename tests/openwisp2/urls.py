import os

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = []

if os.environ.get('SAMPLE_APP', False):
    from openwisp_network_topology.utils import get_visualizer_urls
    from .sample_network_topology.visualizer import views

    urlpatterns += [
        url(r'^topology/', include(get_visualizer_urls(views))),
    ]

urlpatterns += [
    url(r'^', include('openwisp_network_topology.urls')),
    url(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()


if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
