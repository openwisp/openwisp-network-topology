from unittest.mock import patch
from uuid import uuid4

import swapper
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework.views import APIView

from openwisp_network_topology.tasks import handle_update_topology
from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.tests import AssertNumQueriesSubTestMixin

from .utils import CreateGraphObjectsMixin, LoadMixin, UnpublishMixin

Link = swapper.load_model("topology", "Link")
Node = swapper.load_model("topology", "Node")
Snapshot = swapper.load_model("topology", "Snapshot")
Topology = swapper.load_model("topology", "Topology")
Organization = swapper.load_model("openwisp_users", "Organization")
OrganizationUser = swapper.load_model("openwisp_users", "OrganizationUser")
Group = swapper.load_model("openwisp_users", "Group")


class TestApi(
    AssertNumQueriesSubTestMixin,
    CreateGraphObjectsMixin,
    UnpublishMixin,
    LoadMixin,
    TestOrganizationMixin,
    TestCase,
):
    list_url = reverse("network_collection")
    topology_model = Topology
    node_model = Node
    link_model = Link
    snapshot_model = Snapshot

    def setUp(self):
        org = self._get_org()
        self.topology = self._create_topology(organization=org)
        user = self._create_user(username="tester", email="tester@email.com")
        user.groups.set(Group.objects.filter(name="Operator"))
        perm = Permission.objects.filter(codename__endswith="topology")
        user.user_permissions.add(*perm)
        self._create_org_user(user=user, organization=org, is_admin=True)
        self.node1 = self._create_node(
            label="node1",
            addresses=["192.168.0.1"],
            topology=self.topology,
            organization=org,
        )
        self.node2 = self._create_node(
            label="node2",
            addresses=["192.168.0.2"],
            topology=self.topology,
            organization=org,
        )
        self.link = self._create_link(
            source=self.node1, target=self.node2, topology=self.topology
        )
        self.client.force_login(user)

    @property
    def detail_url(self):
        t = self.topology_model.objects.first()
        return reverse("network_graph", args=[t.pk])

    @property
    def receive_url(self):
        t = self.topology_model.objects.first()
        path = reverse("receive_topology", args=[t.pk])
        return f"{path}?key=test"

    @property
    def snapshot_url(self):
        t = self.topology_model.objects.first()
        path = reverse("network_graph_history", args=[t.pk])
        return f"{path}?date={self.snapshot_date}"

    def _set_receive(self):
        t = self.topology_model.objects.first()
        t.parser = "netdiff.NetJsonParser"
        t.strategy = "receive"
        t.key = "test"
        t.expiration_time = 0
        t.save()

    @property
    def snapshot_date(self):
        self.topology_model.objects.first().save_snapshot()
        return self.snapshot_model.objects.first().date

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.data["type"], "NetworkCollection")
        self.assertEqual(len(response.data["collection"]), 1)

    def test_list_topology_filter(self):
        admin = self._create_admin()
        self.client.force_login(admin)
        org2 = self._create_org(name="org2")
        self._create_topology(
            organization=org2, parser="netdiff.OpenvpnParser", strategy="receive"
        )

        with self.subTest("Test without filter"):
            response = self.client.get(self.list_url)
            self.assertEqual(len(response.data["collection"]), 2)

        with self.subTest("Test filter with parser"):
            response = self.client.get(f"{self.list_url}?parser=netdiff.OpenvpnParser")
            self.assertEqual(len(response.data["collection"]), 1)

        with self.subTest("Test filter with organization"):
            response = self.client.get(f"{self.list_url}?organization={org2.pk}")
            self.assertEqual(len(response.data["collection"]), 1)

        with self.subTest("Test filter with organization slug"):
            response = self.client.get(f"{self.list_url}?organization_slug={org2.slug}")
            self.assertEqual(len(response.data["collection"]), 1)

        with self.subTest("Test filter with strategy"):
            response = self.client.get(f"{self.list_url}?strategy=receive")
            self.assertEqual(len(response.data["collection"]), 1)

    def test_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.data["type"], "NetworkGraph")

    def test_list_include_unpublished(self):
        self._unpublish()
        path = f"{self.list_url}?include_unpublished=true"
        response = self.client.get(path)
        self.assertEqual(len(response.data["collection"]), 1)

        path = f"{self.list_url}?published=true"
        response = self.client.get(path)
        self.assertEqual(len(response.data["collection"]), 0)

    def test_detail_unpublished_topology(self):
        self._unpublish()
        with self.subTest("Test view returns 404 for unpublished topology"):
            response = self.client.get(self.detail_url)
            self.assertEqual(response.status_code, 404)

        with self.subTest('Test "include_unpublished" filter'):
            path = f"{self.detail_url}?include_unpublished=true"
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)

    def test_receive(self):
        self._set_receive()
        self.node_model.objects.all().delete()
        data = self._load("static/netjson-1-link.json")
        response = self.client.post(self.receive_url, data, content_type="text/plain")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "data received successfully")
        self.assertEqual(self.node_model.objects.count(), 2)
        self.assertEqual(self.link_model.objects.count(), 1)

    @patch("openwisp_network_topology.tasks.handle_update_topology.delay")
    def test_background_topology_update_task(self, mocked_task):
        self._set_receive()
        self.node_model.objects.all().delete()
        topology = self.topology_model.objects.first()
        data = self._load("static/netjson-1-link.json")
        response = self.client.post(self.receive_url, data, content_type="text/plain")
        mocked_task.assert_called_once_with(topology.pk, topology.diff(data))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "data received successfully")

    @patch("openwisp_network_topology.tasks.logger.warning")
    def test_background_topology_update_task_warning(self, mock_warn):
        invalid_topology_pk = str(uuid4())
        data = {"test_key": "test_value"}
        handle_update_topology(invalid_topology_pk, data)
        mock_warn.assert_called_once_with(
            f'handle_update_topology("{invalid_topology_pk}") failed: Topology matching query does not exist.'
        )

    @patch("openwisp_network_topology.tasks.handle_update_topology.delay")
    def test_handle_update_topology_400_unrecognized_format(self, mocked_task):
        self._set_receive()
        self.node_model.objects.all().delete()
        data = "WRONG"
        response = self.client.post(self.receive_url, data, content_type="text/plain")
        mocked_task.assert_not_called()
        self.assertEqual(response.status_code, 400)
        self.assertIn("not recognized", response.data["detail"])

    def test_receive_404(self):
        # topology is set to FETCH strategy
        response = self.client.post(self.receive_url, content_type="text/plain")
        self.assertEqual(response.status_code, 404)

    def test_receive_415(self):
        self._set_receive()
        data = self._load("static/netjson-1-link.json")
        response = self.client.post(
            self.receive_url, data, content_type="application/xml"
        )
        self.assertEqual(response.status_code, 415)

    def test_receive_400_missing_key(self):
        self._set_receive()
        data = self._load("static/netjson-1-link.json")
        response = self.client.post(
            self.receive_url.replace("?key=test", ""), data, content_type="text/plain"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("missing required", response.data["detail"])

    def test_receive_400_unrecognized_format(self):
        self._set_receive()
        self.node_model.objects.all().delete()
        data = "WRONG"
        response = self.client.post(self.receive_url, data, content_type="text/plain")
        self.assertEqual(response.status_code, 400)
        self.assertIn("not recognized", response.data["detail"])

    def test_receive_403(self):
        self._set_receive()
        data = self._load("static/netjson-1-link.json")
        response = self.client.post(
            self.receive_url.replace("?key=test", "?key=wrong"),
            data,
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, 403)

    def test_receive_options(self):
        self._set_receive()
        response = self.client.options(self.receive_url)
        self.assertEqual(response.data["parses"], ["text/plain"])

    def test_snapshot(self):
        response = self.client.get(self.snapshot_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["type"], "NetworkGraph")

    def test_snapshot_missing_date_400(self):
        date = self.snapshot_date
        response = self.client.get(
            self.snapshot_url.replace("?date={0}".format(date), "")
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], 'missing required "date" parameter')

    def test_snapshot_invalid_date_403(self):
        date = self.snapshot_date
        url = self.snapshot_url.replace("?date={0}".format(date), "?date=wrong-date")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["detail"], "invalid date supplied")

    def test_snapshot_no_snapshot_404(self):
        date = self.snapshot_date
        url = self.snapshot_url.replace("?date={0}".format(date), "?date=2001-01-01")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("no snapshot found", response.data["detail"])

    def _test_api_with_unauthenticated_user(self, url):
        self.client.logout()
        r = self.client.get(url)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(
            r.data["detail"], "Authentication credentials were not provided."
        )
        self.assertEqual(len(r.data), 1)

    def _test_api_with_not_a_manager_user(self, user, url, has_detail=True):
        OrganizationUser.objects.filter(user=user).delete()
        perm = Permission.objects.filter(codename__endswith="topology")
        user.user_permissions.add(*perm)
        self.client.force_login(user)
        r = self.client.get(url)
        if not has_detail:
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.data["type"], "NetworkCollection")
            self.assertEqual(len(r.data["collection"]), 0)
            self.assertNotEqual(Topology.objects.all().count(), 0)
        else:
            detail = (
                "User is not a manager of the organization to "
                "which the requested resource belongs."
            )
            self.assertEqual(r.status_code, 403)
            self.assertEqual(r.data["detail"], detail)
            self.assertEqual(len(r.data), 1)

    def _test_api_with_not_permitted_user(self, user, url):
        t = self.topology_model.objects.first()
        self._create_org_user(user=user, organization=t.organization, is_admin=True)
        self.client.force_login(user)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(
            r.data["detail"], "You do not have permission to perform this action."
        )
        self.assertEqual(len(r.data), 1)

    def test_modelpermission_class_with_change_perm(self):
        t = self.topology_model.objects.first()
        user = self._create_user(username="list-user", email="list@email.com")
        self._create_org_user(user=user, organization=t.organization, is_admin=True)
        change_perm = Permission.objects.filter(codename="change_topology")
        user.user_permissions.add(*change_perm)
        self.client.force_login(user)
        with self.subTest("List url"):
            url = self.list_url
            with self.assertNumQueries(7):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        with self.subTest("Detail url"):
            url = self.detail_url
            with self.assertNumQueries(7):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_modelpermission_class_with_view_perm(self):
        t = self.topology_model.objects.first()
        user = self._create_user(username="list-user", email="list@email.com")
        self._create_org_user(user=user, organization=t.organization, is_admin=True)
        view_perm = Permission.objects.filter(codename="view_topology")
        user.user_permissions.add(*view_perm)
        self.client.force_login(user)
        with self.subTest("List url"):
            url = self.list_url
            with self.assertNumQueries(7):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        with self.subTest("Detail url"):
            url = self.detail_url
            with self.assertNumQueries(7):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_modelpermission_class_with_no_perm(self):
        t = self.topology_model.objects.first()
        user = self._create_user(username="list-user", email="list@email.com")
        self._create_org_user(user=user, organization=t.organization, is_admin=True)
        self.client.force_login(user)
        with self.subTest("List url"):
            url = self.list_url
            with self.assertNumQueries(4):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 403)
        with self.subTest("Detail url"):
            url = self.detail_url
            with self.assertNumQueries(4):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    def test_list_with_auth_enabled(self):
        user = self._create_user(username="list-user", email="list@email.com")
        with self.subTest("test api with unauthenticated user"):
            self._test_api_with_unauthenticated_user(self.list_url)

        with self.subTest("test api with not a permitted user"):
            self._test_api_with_not_permitted_user(user, self.list_url)

        with self.subTest("test api with not a member user"):
            self._test_api_with_not_a_manager_user(user, self.list_url)

    def test_detail_with_auth_enabled(self):
        user = self._create_user(username="detail-user", email="detail@email.com")
        with self.subTest("test api with unauthenticated user"):
            self._test_api_with_unauthenticated_user(self.detail_url)

        with self.subTest("test api with not a permitted user"):
            self._test_api_with_not_permitted_user(user, self.detail_url)

        with self.subTest("test api with not a member user"):
            self._test_api_with_not_a_manager_user(user, self.detail_url)

    def test_snapshot_with_auth_enabled(self):
        user = self._create_user(username="snapshot-user", email="snapshot@email.com")
        with self.subTest("test api with unauthenticated user"):
            self._test_api_with_unauthenticated_user(self.snapshot_url)

        with self.subTest("test api with not a permitted user"):
            self._test_api_with_not_permitted_user(user, self.snapshot_url)

        with self.subTest("test api with not a member user"):
            self._test_api_with_not_a_manager_user(user, self.snapshot_url)

    def _successful_api_tests(self):
        with self.subTest("test receive"):
            self._set_receive()
            self.node_model.objects.all().delete()
            data = self._load("static/netjson-1-link.json")
            response = self.client.post(
                self.receive_url, data, content_type="text/plain"
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["detail"], "data received successfully")
            self.assertEqual(self.node_model.objects.count(), 2)
            self.assertEqual(self.link_model.objects.count(), 1)

        with self.subTest("test history"):
            response = self.client.get(self.snapshot_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["type"], "NetworkGraph")

    @patch.object(APIView, "get_permissions", return_value=[])
    @patch.object(APIView, "get_authenticators", return_value=[])
    def test_api_with_auth_disabled(self, perm_mocked, auth_mocked):
        user = self._get_user(username="tester")
        self.client.logout()
        self._successful_api_tests()
        self.client.force_login(user)

    def test_superuser_with_api_auth_enabled(self):
        user = self._create_admin(username="superapi", email="superapi@email.com")
        self.client.force_login(user)
        self._successful_api_tests()

    @patch.object(APIView, "get_permissions", return_value=[])
    @patch.object(APIView, "get_authenticators", return_value=[])
    def test_superuser_with_api_auth_disabled(self, perm_mocked, auth_mocked):
        user = self._create_admin(username="superapi", email="superapi@email.com")
        self.client.force_login(user)
        self._successful_api_tests()

    def test_fetch_topology_create_api(self):
        path = reverse("network_collection")
        data = {
            "label": "test-fetch-topology",
            "organization": self._get_org().id,
            "parser": "netdiff.OlsrParser",
            "strategy": "fetch",
            "url": "http://127.0.0.1:9090",
            "published": True,
        }
        with self.assertNumQueries(12):
            response = self.client.post(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["label"], "test-fetch-topology")
        self.assertEqual(response.data["parser"], "netdiff.OlsrParser")

    def test_receive_topology_create_api(self):
        path = reverse("network_collection")
        data = {
            "label": "test-receive-topology",
            "organization": self._get_org().pk,
            "parser": "netdiff.OlsrParser",
            "strategy": "receive",
            "key": "A3DJ62jhd49",
            "expiration_time": 360,
            "published": True,
        }
        with self.assertNumQueries(12):
            response = self.client.post(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["label"], "test-receive-topology")
        self.assertEqual(response.data["parser"], "netdiff.OlsrParser")
        self.assertEqual(response.data["key"], "A3DJ62jhd49")

    def test_topology_detail_receive_url_api(self):
        org1 = self._get_org()
        topo = self._create_topology(organization=org1)
        path = reverse("network_graph", args=(topo.pk,))
        r_path = reverse("receive_topology", args=[topo.pk])
        receive_url = "http://testserver{0}?key={1}".format(r_path, topo.key)
        with self.assertNumQueries(7):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["receive_url"], receive_url)

    def test_topology_receive_no_key_create_api(self):
        path = reverse("network_collection")
        data = {
            "label": "test-receive-topology",
            "organization": self._get_org().pk,
            "parser": "netdiff.OlsrParser",
            "strategy": "receive",
            "key": "",
            "expiration_time": 360,
            "published": True,
        }
        with self.assertNumQueries(7):
            response = self.client.post(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "a key must be specified when using RECEIVE strategy", str(response.content)
        )

    def test_get_topology_detail_api(self):
        org1 = self._get_org()
        topo = self._create_topology(organization=org1)
        path = reverse("network_graph", args=(topo.pk,))
        with self.assertNumQueries(7):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)

    def test_get_topology_detail_with_link_api(self):
        path = reverse("network_graph", args=(self.topology.pk,))
        with self.assertNumQueries(7):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data["links"], [])

    def test_put_topology_detail_api(self):
        path = reverse("network_graph", args=[self.topology.pk])
        data = {
            "label": "ChangeTestNetwork",
            "organization": self._get_org().pk,
            "parser": "netdiff.OlsrParser",
        }
        with self.assertNumQueries(12):
            response = self.client.put(path, data, content_type="application/json")
        self.topology.refresh_from_db()
        self.assertEqual(self.topology.label, "ChangeTestNetwork")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["label"], "ChangeTestNetwork")
        self.assertEqual(response.data["type"], "NetworkGraph")

    def test_change_strategy_fetch_api_400(self):
        org1 = self._get_org()
        topo = self._create_topology(organization=org1)
        path = reverse("network_graph", args=(topo.pk,))
        data = {
            "label": "ChangeTestNetwork",
            "organization": org1.pk,
            "parser": "netdiff.OlsrParser",
            "strategy": "fetch",
            "url": "",
        }
        with self.assertNumQueries(6):
            response = self.client.put(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "An url must be specified when using FETCH strategy", str(response.content)
        )

    def test_change_strategy_receive_api_400(self):
        org1 = self._get_org()
        topo = self._create_topology(organization=org1)
        path = reverse("network_graph", args=(topo.pk,))
        data = {
            "label": "ChangeTestNetwork",
            "organization": self._get_org().pk,
            "parser": "netdiff.OlsrParser",
            "strategy": "receive",
            "key": "",
        }
        with self.assertNumQueries(6):
            response = self.client.put(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "A key must be specified when using RECEIVE strategy", str(response.content)
        )

    def test_change_strategy_fetch_api_200(self):
        org1 = self._get_org()
        topo = self._create_topology(organization=org1, strategy="receive")
        path = reverse("network_graph", args=[topo.pk])
        self.assertEqual(topo.strategy, "receive")
        data = {
            "label": "ChangeTestNetwork",
            "organization": org1.pk,
            "parser": "netdiff.OlsrParser",
            "strategy": "fetch",
            "url": "http://127.0.0.1:9090",
        }
        with self.assertNumQueries(12):
            response = self.client.put(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["strategy"], "fetch")
        topo.refresh_from_db()
        self.assertEqual(topo.strategy, "fetch")

    def test_change_strategy_receive_api_200(self):
        org1 = self._get_org()
        topo = self._create_topology(organization=org1, strategy="fetch")
        path = reverse("network_graph", args=[topo.pk])
        self.assertEqual(topo.strategy, "fetch")
        data = {
            "label": "ChangeTestNetwork",
            "organization": org1.pk,
            "parser": "netdiff.OlsrParser",
            "strategy": "receive",
            "key": 12345,
        }
        with self.assertNumQueries(12):
            response = self.client.put(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["strategy"], "receive")
        topo.refresh_from_db()
        self.assertEqual(topo.strategy, "receive")

    def test_patch_topology_detail_api(self):
        path = reverse("network_graph", args=(self.topology.pk,))
        data = {
            "label": "ChangeTestNetwork",
        }
        with self.assertNumQueries(11):
            response = self.client.patch(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["label"], "ChangeTestNetwork")

    def test_delete_topology_api(self):
        path = reverse("network_graph", args=(self.topology.pk,))
        response = self.client.delete(path)
        self.assertEqual(response.status_code, 204)

    def test_topology_filter_by_org_api(self):
        org1 = self._create_org(name="org1")
        org2 = self._create_org(name="org2")
        topo1 = self._create_topology(label="topo1", organization=org1)
        topo2 = self._create_topology(label="topo2", organization=org2)
        user1 = self._create_user(username="test-filter", email="test@filter.com")
        self._create_org_user(user=user1, organization=org1, is_admin=True)
        view_perm = Permission.objects.filter(codename="view_topology")
        user1.user_permissions.add(*view_perm)
        self.client.force_login(user1)
        with self.subTest("test network collection view"):
            path = reverse("network_collection")
            with self.assertNumQueries(7):
                response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(str(topo1.id), str(response.content))
            self.assertNotIn(str(topo2.id), str(response.content))

        with self.subTest("test network graph view"):
            # Get the topology graph view of member org 200
            path = reverse("network_graph", args=(topo1.pk,))
            with self.assertNumQueries(7):
                response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["id"], str(topo1.id))

            # Get the topology graph view of different org 404
            path = reverse("network_graph", args=(topo2.pk,))
            with self.assertNumQueries(5):
                response = self.client.get(path)
            self.assertEqual(response.status_code, 404)

    def test_topology_filter_fields_by_org_api(self):
        org1 = self._get_org()
        user1 = self._create_user(username="test-filter", email="test@filter.com")
        self._create_org_user(user=user1, organization=org1, is_admin=True)
        topo_perm = Permission.objects.filter(codename__endswith="topology")
        user1.user_permissions.add(*topo_perm)
        self.client.force_login(user1)
        with self.subTest("test network collection view"):
            path = reverse("network_collection")
            with self.assertNumQueries(8):
                response = self.client.get(path, {"format": "api"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Organization.objects.count(), 2)
            self.assertContains(response, "test org</option>")
            self.assertNotContains(response, "default</option>")

        with self.subTest("test network graph view"):
            topo1 = self._create_topology(label="topo1", organization=org1)
            path = reverse("network_graph", args=(topo1.pk,))
            with self.assertNumQueries(14):
                response = self.client.get(path, {"format": "api"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Organization.objects.count(), 2)
            self.assertContains(response, "test org</option>")
            self.assertNotContains(response, "default</option>")

    def test_node_list_api(self):
        path = reverse("node_list")
        with self.assertNumQueries(6):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_node_list_multitenancy(self):
        path = reverse("node_list")
        org2 = self._create_org(name="org2")
        t2 = self._create_topology(organization=org2)
        self._create_node(
            label="node2", addresses=["192.168.0.2"], topology=t2, organization=org2
        )
        self.assertEqual(Node.objects.count(), 3)
        with self.assertNumQueries(6):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        # Only nodes related to user's organization are returned
        self.assertEqual(response.data["count"], 2)

    def test_node_list_filter(self):
        admin = self._get_admin()
        self.client.force_login(admin)
        org1 = self._get_org()
        org2 = self._create_org(name="org2")
        t2 = self._create_topology(organization=org2)
        self._create_node(
            label="node2", addresses=["192.168.0.2"], topology=t2, organization=org2
        )
        path = reverse("node_list")

        with self.subTest("Test list without filters"):
            response = self.client.get(path)
            self.assertEqual(response.data["count"], 3)

        with self.subTest("Test filter by organization"):
            response = self.client.get(f"{path}?organization={org1.pk}")
            self.assertEqual(response.data["count"], 2)

        with self.subTest("Test filter by organization slug"):
            response = self.client.get(f"{path}?organization_slug={org1.slug}")
            self.assertEqual(response.data["count"], 2)

        with self.subTest("Test filter by topology"):
            response = self.client.get(f"{path}?topology={t2.pk}")
            self.assertEqual(response.data["count"], 1)

    def test_node_create_api(self):
        path = reverse("node_list")
        data = {
            "topology": self.topology.pk,
            "label": "test-node",
            "addresses": ["192.168.0.1"],
            "properties": {},
            "user_properties": {},
        }
        with self.assertNumQueries(13):
            response = self.client.post(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["topology"], self.topology.pk)
        self.assertEqual(response.data["label"], "test-node")
        self.assertEqual(response.data["addresses"], ["192.168.0.1"])

    def test_node_create_api_shared_topology(self):
        admin = self._get_admin()
        self.client.force_login(admin)
        topology = self._create_topology(organization=None)
        org = self._get_org()
        data = {
            "topology": topology.pk,
            "label": "test-node",
            "addresses": ["192.168.0.1"],
            "properties": {},
            "user_properties": {},
            "organization": org.pk,
        }
        path = reverse("node_list")
        with self.assertNumQueries(11):
            response = self.client.post(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["topology"], topology.pk)
        self.assertEqual(response.data["organization"], org.pk)

    def test_node_detail_api(self):
        path = reverse("node_detail", args=(self.node1.pk,))
        with self.assertNumQueries(6):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.node1.pk))
        self.assertEqual(response.data["label"], self.node1.label)
        self.assertEqual(response.data["topology"], self.node1.topology.pk)
        self.assertEqual(response.data["organization"], self.node1.organization.pk)
        self.assertEqual(response.data["addresses"], self.node1.addresses)
        self.assertEqual(response.data["properties"], self.node1.properties)
        self.assertEqual(response.data["user_properties"], self.node1.user_properties)
        self.assertIn("created", response.data)
        self.assertIn("modified", response.data)

    def test_node_put_api(self):
        data = {
            "topology": self.topology.pk,
            "label": "change-node",
            "addresses": ["192.168.0.1", "192.168.0.2"],
            "properties": {},
            "user_properties": {},
        }
        path = reverse("node_detail", args=(self.node1.pk,))
        with self.assertNumQueries(13):
            response = self.client.put(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["label"], "change-node")
        self.assertEqual(response.data["addresses"], ["192.168.0.1", "192.168.0.2"])

    def test_node_patch_api(self):
        path = reverse("node_detail", args=(self.node1.pk,))
        data = {"label": "change-node"}
        with self.assertNumQueries(12):
            response = self.client.patch(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["label"], "change-node")

    def test_node_delete_api(self):
        node = self._create_node(
            label="delete-node", addresses=["192.168.0.1"], topology=self.topology
        )
        path = reverse("node_detail", args=(node.pk,))
        response = self.client.delete(path)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Node.objects.filter(label="delete-node").count(), 0)

    def test_link_list_api(self):
        path = reverse("link_list")
        with self.assertNumQueries(6):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_link_list_filters(self):
        admin = self._get_admin()
        self.client.force_login(admin)
        org1 = self._get_org()
        org2 = self._create_org(name="org2")
        t2 = self._create_topology(organization=org2)
        node1 = self._create_node(
            label="node2", addresses=["192.168.0.2"], topology=t2, organization=org2
        )
        node2 = self._create_node(
            label="node2", addresses=["192.168.0.3"], topology=t2, organization=org2
        )
        self._create_link(source=node1, target=node2, topology=t2, status="down")
        path = reverse("link_list")

        with self.subTest("Test list without filters"):
            response = self.client.get(path)
            self.assertEqual(response.data["count"], 2)

        with self.subTest("Test filter by organization"):
            response = self.client.get(f"{path}?organization={org1.pk}")
            self.assertEqual(response.data["count"], 1)

        with self.subTest("Test filter by organization slug"):
            response = self.client.get(f"{path}?organization_slug={org1.slug}")
            self.assertEqual(response.data["count"], 1)

        with self.subTest("Test filter by topology"):
            response = self.client.get(f"{path}?topology={t2.pk}")
            self.assertEqual(response.data["count"], 1)

        with self.subTest("Test filter by status"):
            response = self.client.get(f"{path}?status=down")
            self.assertEqual(response.data["count"], 1)

    def test_link_create_api(self):
        path = reverse("link_list")
        node3 = self._create_node(label="node3", topology=self.topology)
        data = {
            "topology": self.topology.pk,
            "source": self.node1.pk,
            "target": node3.pk,
            "cost": 1.0,
            "properties": {},
            "user_properties": {},
        }
        with self.assertNumQueries(16):
            response = self.client.post(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["topology"], self.topology.pk)
        self.assertEqual(response.data["status"], "up")
        self.assertEqual(response.data["source"], self.node1.pk)
        self.assertEqual(response.data["target"], node3.pk)

    def test_link_create_with_wrong_value_format_api(self):
        path = reverse("link_list")
        node3 = self._create_node(label="node3", topology=self.topology)
        data = {
            "topology": self.topology.pk,
            "source": self.node1.pk,
            "target": node3.pk,
            "cost": 1.0,
            "properties": 0,
            "user_properties": 122343,
        }
        with self.assertNumQueries(7):
            response = self.client.post(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["properties"][0].title(),
            "Value Must Be Valid Json Or Key, Valued Pair.",
        )
        self.assertEqual(
            response.data["user_properties"][0].title(),
            "Value Must Be Valid Json Or Key, Valued Pair.",
        )

    def test_link_detail_api(self):
        path = reverse("link_detail", args=(self.link.pk,))
        with self.assertNumQueries(6):
            response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.link.pk))
        self.assertEqual(response.data["topology"], self.topology.pk)
        self.assertEqual(response.data["source"], self.node1.pk)
        self.assertEqual(response.data["target"], self.node2.pk)
        self.assertEqual(response.data["organization"], self.link.organization.pk)
        self.assertEqual(response.data["status"], self.link.status)
        self.assertEqual(response.data["cost"], self.link.cost)
        self.assertEqual(response.data["cost_text"], self.link.cost_text)
        self.assertEqual(response.data["properties"], self.link.properties)
        self.assertEqual(response.data["user_properties"], self.link.user_properties)
        self.assertIn("created", response.data)
        self.assertIn("modified", response.data)

    def test_link_put_api(self):
        path = reverse("link_detail", args=(self.link.pk,))
        data = {
            "topology": self.topology.pk,
            "source": self.node1.pk,
            "target": self.node2.pk,
            "cost": 21.0,
            "properties": {},
            "user_properties": {"user": "tester"},
        }
        with self.assertNumQueries(16):
            response = self.client.put(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["cost"], 21.0)
        self.assertEqual(response.data["properties"], {})
        self.assertEqual(response.data["user_properties"], {"user": "tester"})

    def test_link_patch_api(self):
        path = reverse("link_detail", args=(self.link.pk,))
        data = {"cost": 50.0}
        with self.assertNumQueries(13):
            response = self.client.patch(path, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["cost"], 50.0)

    def test_link_delete_api(self):
        self.assertEqual(Link.objects.count(), 1)
        path = reverse("link_detail", args=(self.link.pk,))
        response = self.client.delete(path)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Link.objects.count(), 0)
