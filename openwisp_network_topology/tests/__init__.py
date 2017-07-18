from openwisp_users.models import Organization


class CreateOrgMixin(object):
    def _create_org(self, **kwargs):
        options = dict(name='test-organization')
        options.update(kwargs)
        org = Organization(**options)
        org.save()
        return org
