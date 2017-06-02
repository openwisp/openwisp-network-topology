from django.conf.urls import include, url

from .api import urls as api

urlpatterns = [
    url(r'^accounts/', include('openwisp_users.accounts.urls')),
    url(r'^api/', include(api)),
]
