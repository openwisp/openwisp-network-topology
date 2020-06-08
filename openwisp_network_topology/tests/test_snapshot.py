import swapper
from django.test import TestCase

Snapshot = swapper.load_model('topology', 'Snapshot')


class TestSnapshot(TestCase):
    snapshot_model = Snapshot

    def test_str(self):
        s = self.snapshot_model.objects.first()
        self.assertIsInstance(str(s), str)
