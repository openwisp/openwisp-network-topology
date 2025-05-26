import json
import sys
from contextlib import contextmanager
from datetime import timedelta
from io import StringIO

import responses
import swapper
from django.core.management import call_command
from django.test import TestCase
from django.utils.timezone import now

from .. import settings as app_settings
from .utils import CreateGraphObjectsMixin, CreateOrgMixin, LoadMixin

Organization = swapper.load_model("openwisp_users", "Organization")
Link = swapper.load_model("topology", "Link")
Node = swapper.load_model("topology", "Node")
Snapshot = swapper.load_model("topology", "Snapshot")
Topology = swapper.load_model("topology", "Topology")


@contextmanager
def redirect_stdout(stream):
    sys.stdout = stream
    try:
        yield
    finally:
        sys.stdout = sys.__stdout__


class TestUtils(CreateGraphObjectsMixin, CreateOrgMixin, LoadMixin, TestCase):
    """
    tests for django_netjsongraph.utils
    """

    topology_model = Topology
    node_model = Node
    link_model = Link
    snapshot_model = Snapshot
    organization_model = Organization
    maxDiff = None

    def setUp(self):
        org = self._create_org()
        t = self._create_topology(organization=org)
        self._create_node(
            label="node1", addresses=["192.168.0.1"], topology=t, organization=org
        )
        self._create_node(
            label="node2", addresses=["192.168.0.2"], topology=t, organization=org
        )

    def _create_link(self, **kwargs):
        org = self.organization_model.objects.first()
        options = dict(cost="1", cost_text="one", properties={}, organization=org)
        options.update(kwargs)
        link = self.link_model(**options)
        link.full_clean()
        link.save()
        return link

    @responses.activate
    def test_update_all_method(self):
        t = self.topology_model.objects.first()
        t.parser = "netdiff.NetJsonParser"
        t.save()
        responses.add(
            responses.GET,
            "http://127.0.0.1:9090",
            body=self._load("static/netjson-1-link.json"),
            content_type="application/json",
        )
        self.node_model.objects.all().delete()
        self.topology_model.update_all("testnetwork")
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)
        # test exception
        t.url = t.url.replace("9090", "9091")
        t.save()
        self.node_model.objects.all().delete()
        self.link_model.objects.all().delete()
        responses.add(
            responses.GET,
            "http://127.0.0.1:9091",
            body=self._load("static/netjson-invalid.json"),
            content_type="application/json",
        )
        # capture output
        output = StringIO()
        with redirect_stdout(output):
            self.topology_model.update_all()

        self.assertEqual(self.node_model.objects.count(), 1)
        self.assertEqual(self.link_model.objects.count(), 0)
        self.assertIn("Failed to", output.getvalue())

    @responses.activate
    def test_update_topology_command(self):
        t = self.topology_model.objects.first()
        t.parser = "netdiff.NetJsonParser"
        t.save()
        responses.add(
            responses.GET,
            "http://127.0.0.1:9090",
            body=self._load("static/netjson-1-link.json"),
            content_type="application/json",
        )
        self.node_model.objects.all().delete()
        self.topology_model.update_all()
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)
        # test exception
        t.url = t.url.replace("9090", "9091")
        t.save()
        self.node_model.objects.all().delete()
        self.link_model.objects.all().delete()
        responses.add(
            responses.GET,
            "http://127.0.0.1:9091",
            body=self._load("static/netjson-invalid.json"),
            content_type="application/json",
        )
        # capture output
        output = StringIO()
        with redirect_stdout(output):
            call_command("update_topology")

        self.assertEqual(self.node_model.objects.count(), 1)
        self.assertEqual(self.link_model.objects.count(), 0)
        self.assertIn("Failed to", output.getvalue())

    @responses.activate
    def test_update_all_method_unpublished(self):
        t = self.topology_model.objects.first()
        t.published = False
        t.parser = "netdiff.NetJsonParser"
        t.save()
        responses.add(
            responses.GET,
            "http://127.0.0.1:9090",
            body=self._load("static/netjson-1-link.json"),
            content_type="application/json",
        )
        self.node_model.objects.all().delete()
        self.topology_model.update_all()
        self.assertEqual(self.node_model.objects.count(), 0)
        self.assertEqual(self.link_model.objects.count(), 0)

    @responses.activate
    def test_delete_expired_links(self):
        t = self.topology_model.objects.first()
        t.parser = "netdiff.NetJsonParser"
        t.save()
        # should not delete
        almost_expired_date = now() - timedelta(days=app_settings.LINK_EXPIRATION - 10)
        n1 = self.node_model.objects.all()[0]
        n2 = self.node_model.objects.all()[1]
        link = self._create_link(
            source=n1, target=n2, cost=1, status="down", topology=t
        )
        self.link_model.objects.filter(pk=link.pk).update(
            created=almost_expired_date, modified=almost_expired_date
        )
        empty_topology = json.dumps(
            {
                "type": "NetworkGraph",
                "protocol": "OLSR",
                "version": "0.8",
                "metric": "ETX",
                "nodes": [],
                "links": [],
            }
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:9090",
            body=empty_topology,
            content_type="application/json",
        )
        self.topology_model.update_all("testnetwork")
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)
        # should delete
        expired_date = now() - timedelta(days=app_settings.LINK_EXPIRATION + 10)
        self.link_model.objects.filter(pk=link.pk).update(
            created=expired_date, modified=expired_date
        )
        self.topology_model.update_all("testnetwork")
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 0)

    @responses.activate
    def test_delete_expired_nodes(self):
        NODE_EXPIRATION = getattr(app_settings, "NODE_EXPIRATION")
        # Test with the default value(False)
        # Should not delete
        setattr(app_settings, "NODE_EXPIRATION", False)
        t = self.topology_model.objects.first()
        t.parser = "netdiff.NetJsonParser"
        t.save()
        expired_date = now() - timedelta(days=60)
        n1 = self.node_model.objects.all()[0]
        n2 = self.node_model.objects.all()[1]
        self.node_model.objects.filter(pk=n1.pk).update(
            created=expired_date, modified=expired_date
        )
        self.node_model.objects.filter(pk=n2.pk).update(
            created=expired_date, modified=expired_date
        )
        empty_topology = json.dumps(
            {
                "type": "NetworkGraph",
                "protocol": "OLSR",
                "version": "0.8",
                "metric": "ETX",
                "nodes": [],
                "links": [],
            }
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:9090",
            body=empty_topology,
            content_type="application/json",
        )
        self.topology_model.update_all("testnetwork")
        self.assertEqual(self.node_model.objects.count(), 2)

        # Test with a custom value
        # Should delete
        setattr(app_settings, "NODE_EXPIRATION", 60)
        expired_date = now() - timedelta(days=app_settings.NODE_EXPIRATION + 10)
        self.node_model.objects.filter(pk=n1.pk).update(
            created=expired_date, modified=expired_date
        )
        self.node_model.objects.filter(pk=n2.pk).update(
            created=expired_date, modified=expired_date
        )
        self.topology_model.update_all("testnetwork")
        self.assertEqual(self.node_model.objects.count(), 0)
        self.assertEqual(self.link_model.objects.count(), 0)
        # Set the setting to it's original value
        setattr(app_settings, "NODE_EXPIRATION", NODE_EXPIRATION)

    @responses.activate
    def test_delete_expired_disabled(self):
        t = self.topology_model.objects.first()
        t.parser = "netdiff.NetJsonParser"
        t.save()
        n1 = self.node_model.objects.all()[0]
        n2 = self.node_model.objects.all()[1]
        link = self._create_link(
            source=n1, target=n2, cost=1, status="down", topology=t
        )
        expired_date = now() - timedelta(days=app_settings.LINK_EXPIRATION + 10)
        self.link_model.objects.filter(pk=link.pk).update(
            created=expired_date, modified=expired_date
        )
        empty_topology = json.dumps(
            {
                "type": "NetworkGraph",
                "protocol": "OLSR",
                "version": "0.8",
                "metric": "ETX",
                "nodes": [],
                "links": [],
            }
        )
        responses.add(
            responses.GET,
            "http://127.0.0.1:9090",
            body=empty_topology,
            content_type="application/json",
        )
        ORIGINAL_LINK_EXPIRATION = int(app_settings.LINK_EXPIRATION)
        app_settings.LINK_EXPIRATION = False
        self.topology_model.update_all("testnetwork")
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)
        app_settings.LINK_EXPIRATION = ORIGINAL_LINK_EXPIRATION

    def test_save_snapshot_all_method(self, **kwargs):
        org = self._create_org()
        options = dict(organization=org)
        options.update(**kwargs)
        self.assertEqual(self.snapshot_model.objects.count(), 0)
        self.topology_model.save_snapshot_all("testnetwork")
        self.assertEqual(self.snapshot_model.objects.count(), 1)
        self._create_topology(**options)
        self.topology_model.save_snapshot_all()
        self.assertEqual(self.snapshot_model.objects.count(), 2)

    def test_save_snapshot_command(self):
        self.assertEqual(self.snapshot_model.objects.count(), 0)
        output = StringIO()
        with redirect_stdout(output):
            call_command("save_snapshot")
        self.assertEqual(self.snapshot_model.objects.count(), 1)
