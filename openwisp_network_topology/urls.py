from django.conf.urls import include, url

from .api import urls as api
from .visualizer import urls as visualizer_urls

urlpatterns = [
    url(r'^accounts/', include('openwisp_users.accounts.urls')),
    url(r'^api/v1/', include(api)),
    url(r'^topology/', include(visualizer_urls)),
]
