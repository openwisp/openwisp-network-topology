from django.conf.urls import include, url

from openwisp_network_topology.admin_theme.admin import admin, openwisp_admin
from openwisp_network_topology import urls as urls

openwisp_admin()

urlpatterns = [
    url(r'^', include(urls)),
    url(r'^admin/', include(admin.site.urls)),
]
