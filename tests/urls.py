from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from openwisp_utils.admin_theme.admin import admin, openwisp_admin

openwisp_admin()

urlpatterns = [
    url(r'^', include('openwisp_network_topology.urls')),
    url(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
