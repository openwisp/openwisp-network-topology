from django_netjsongraph.utils import get_visualizer_urls

from . import views

urlpatterns = get_visualizer_urls(views)
