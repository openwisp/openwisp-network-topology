from django.urls import include, path

from .api import urls as api
from .visualizer import urls as visualizer_urls

urlpatterns = [
    path("accounts/", include("openwisp_users.accounts.urls")),
    path("api/v1/", include(api)),
    path("topology/", include(visualizer_urls)),
]
