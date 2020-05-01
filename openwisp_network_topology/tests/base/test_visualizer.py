from django.urls import reverse

from ..utils import UnpublishMixin


class TestVisualizerMixin(UnpublishMixin):
    def test_list(self):
        response = self.client.get(reverse('topology_list'))
        self.assertContains(response, 'TestNetwork')

    def test_detail(self):
        t = self.topology_model.objects.first()
        response = self.client.get(reverse('topology_detail', args=[t.pk]))
        self.assertContains(response, t.pk)
        # ensure switcher is present
        self.assertContains(response, 'njg-switcher')
        self.assertContains(response, 'njg-datepicker')

    def test_list_unpublished(self):
        self._unpublish()
        response = self.client.get(reverse('topology_list'))
        self.assertNotContains(response, 'TestNetwork')

    def test_detail_unpublished(self):
        self._unpublish()
        t = self.topology_model.objects.first()
        response = self.client.get(reverse('topology_detail', args=[t.pk]))
        self.assertEqual(response.status_code, 404)

    def test_detail_uuid_exception(self):
        """
        see https://github.com/netjson/django-netjsongraph/issues/4
        """
        t = self.topology_model.objects.first()
        response = self.client.get(
            reverse('topology_detail', args=['{0}-wrong'.format(t.pk)])
        )
        self.assertEqual(response.status_code, 404)
