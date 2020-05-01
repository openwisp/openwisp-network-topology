# from openwisp_network_topology.api import api_views
from openwisp_network_topology.utils import get_api_urls

from . import views as api_views

urlpatterns = get_api_urls(api_views)
