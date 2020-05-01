from ..utils import LoadMixin, UnpublishMixin


class TestApiMixin(UnpublishMixin, LoadMixin):
    list_url = '/api/topology/'

    @property
    def detail_url(self):
        t = self.topology_model.objects.first()
        return '/api/topology/{0}/'.format(t.pk)

    @property
    def receive_url(self):
        t = self.topology_model.objects.first()
        return '/api/receive/{0}/?key=test'.format(t.pk)

    @property
    def snapshot_url(self):
        t = self.topology_model.objects.first()
        return '/api/topology/{0}/history/?date={1}'.format(t.pk, self.snapshot_date)

    def _set_receive(self):
        t = self.topology_model.objects.first()
        t.parser = 'netdiff.NetJsonParser'
        t.strategy = 'receive'
        t.key = 'test'
        t.expiration_time = 0
        t.save()

    @property
    def snapshot_date(self):
        self.topology_model.objects.first().save_snapshot()
        return self.snapshot_model.objects.first().date

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.data['type'], 'NetworkCollection')
        self.assertEqual(len(response.data['collection']), 1)

    def test_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.data['type'], 'NetworkGraph')

    def test_list_unpublished(self):
        self._unpublish()
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data['collection']), 0)

    def test_detail_unpublished(self):
        self._unpublish()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 404)

    def test_receive(self):
        self._set_receive()
        self.node_model.objects.all().delete()
        data = self._load('static/netjson-1-link.json')
        response = self.client.post(self.receive_url, data, content_type='text/plain')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'data received successfully')
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)

    def test_receive_404(self):
        # topology is set to FETCH strategy
        response = self.client.post(self.receive_url, content_type='text/plain')
        self.assertEqual(response.status_code, 404)

    def test_receive_415(self):
        self._set_receive()
        data = self._load('static/netjson-1-link.json')
        response = self.client.post(
            self.receive_url, data, content_type='application/xml'
        )
        self.assertEqual(response.status_code, 415)

    def test_receive_400_missing_key(self):
        self._set_receive()
        data = self._load('static/netjson-1-link.json')
        response = self.client.post(
            self.receive_url.replace('?key=test', ''), data, content_type='text/plain'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('missing required', response.data['detail'])

    def test_receive_400_unrecognized_format(self):
        self._set_receive()
        self.node_model.objects.all().delete()
        data = 'WRONG'
        response = self.client.post(self.receive_url, data, content_type='text/plain')
        self.assertEqual(response.status_code, 400)
        self.assertIn('not recognized', response.data['detail'])

    def test_receive_403(self):
        self._set_receive()
        data = self._load('static/netjson-1-link.json')
        response = self.client.post(
            self.receive_url.replace('?key=test', '?key=wrong'),
            data,
            content_type='text/plain',
        )
        self.assertEqual(response.status_code, 403)

    def test_receive_options(self):
        self._set_receive()
        response = self.client.options(self.receive_url)
        self.assertEqual(response.data['parses'], ['text/plain'])

    def test_snapshot(self):
        response = self.client.get(self.snapshot_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'NetworkGraph')

    def test_snapshot_missing_date_400(self):
        date = self.snapshot_date
        response = self.client.get(
            self.snapshot_url.replace('?date={0}'.format(date), '')
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'missing required "date" parameter')

    def test_snapshot_invalid_date_403(self):
        date = self.snapshot_date
        url = self.snapshot_url.replace('?date={0}'.format(date), '?date=wrong-date')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'invalid date supplied')

    def test_snapshot_no_snapshot_404(self):
        date = self.snapshot_date
        url = self.snapshot_url.replace('?date={0}'.format(date), '?date=2001-01-01')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn('no snapshot found', response.data['detail'])
