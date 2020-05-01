class TestSnapshotMixin(object):
    def test_str(self):
        s = self.snapshot_model.objects.first()
        self.assertIsInstance(str(s), str)
