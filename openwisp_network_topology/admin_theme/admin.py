from django.contrib import admin
from django.utils.translation import ugettext_lazy


def openwisp_admin(site_url=None):
    # <title>
    admin.site.site_title = ugettext_lazy('OpenWISP2 Admin')
    # link to frontend
    admin.site.site_url = site_url
    # h1 text
    admin.site.site_header = ugettext_lazy('OpenWISP')
    # text at the top of the admin index page
    admin.site.index_title = ugettext_lazy('Network administration')
