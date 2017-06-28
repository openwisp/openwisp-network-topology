from django.conf.urls import include, url

from openwisp_network_topology import urls as urls
from openwisp_utils.admin_theme.admin import admin, openwisp_admin

openwisp_admin()

urlpatterns = [
    url(r'^', include(urls)),
    url(r'^admin/', include(admin.site.urls)),
]
