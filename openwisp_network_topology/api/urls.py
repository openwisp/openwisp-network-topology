from django_netjsongraph.utils import get_api_urls

from . import views

urlpatterns = get_api_urls(views)
