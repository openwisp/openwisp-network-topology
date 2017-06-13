from django.conf.urls import include, url
from django.contrib import admin

from openwisp_network_topology import urls as urls

urlpatterns = [
    url(r'^', include(urls)),
    url(r'^admin/', include(admin.site.urls)),
]
