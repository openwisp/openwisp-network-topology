from unittest.mock import patch

import swapper
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from openwisp_users.tests.utils import TestOrganizationMixin

from .. import settings as app_settings
from .utils import CreateGraphObjectsMixin, UnpublishMixin

Node = swapper.load_model("topology", "Node")
Topology = swapper.load_model("topology", "Topology")
OrganizationUser = swapper.load_model("openwisp_users", "OrganizationUser")


class TestVisualizer(
    UnpublishMixin, CreateGraphObjectsMixin, TestOrganizationMixin, TestCase
):
    topology_model = Topology
    node_model = Node

    def setUp(self):
        org = self._create_org()
        user = self._create_admin(username="visualizer", email="visualizer@email.com")
        self._create_org_user(user=user, organization=org)
        self.client.force_login(user)
        t = self._create_topology(organization=org)
        self._create_node(
            label="node1", addresses=["192.168.0.1"], topology=t, organization=org
        )
        self._create_node(
            label="node2", addresses=["192.168.0.2"], topology=t, organization=org
        )

    def test_list(self):
        response = self.client.get(reverse("topology_list"))
        self.assertContains(response, "TestNetwork")

    def test_detail(self):
        t = self.topology_model.objects.first()
        response = self.client.get(reverse("topology_detail", args=[t.pk]))
        self.assertContains(response, t.pk)
        # ensure switcher is present
        self.assertContains(response, "njg-switcher")
        self.assertContains(response, "njg-datepicker")

    def test_list_unpublished(self):
        self._unpublish()
        response = self.client.get(reverse("topology_list"))
        self.assertNotContains(response, "TestNetwork")

    def test_detail_unpublished(self):
        self._unpublish()
        t = self.topology_model.objects.first()
        response = self.client.get(reverse("topology_detail", args=[t.pk]))
        self.assertEqual(response.status_code, 404)

    def test_detail_uuid_exception(self):
        """
        see https://github.com/netjson/django-netjsongraph/issues/4
        """
        t = self.topology_model.objects.first()
        response = self.client.get(
            reverse("topology_detail", args=["{0}-wrong".format(t.pk)])
        )
        self.assertEqual(response.status_code, 404)

    def _test_visualizer_with_unauthenticated_user(self, url):
        self.client.logout()
        r = self.client.get(url)
        self.assertContains(
            r, "Authentication credentials were not provided.", status_code=403
        )

    def _test_visualizer_with_not_a_manager_user(self, user, url, is_detail=False):
        OrganizationUser.objects.filter(user=user).delete()
        perm = Permission.objects.filter(codename__endswith="topology")
        user.user_permissions.add(*perm)
        self.client.force_login(user)
        r = self.client.get(url)
        if is_detail:
            detail = (
                "User is not a manager of the organization to "
                "which the requested resource belongs."
            )
            self.assertContains(r, detail, status_code=403)
        else:
            self.assertEqual(r.status_code, 200)
            self.assertNotContains(r, "TestNetwork")
            self.assertNotEqual(Topology.objects.all().count(), 0)

    def _test_visualizer_with_not_permitted_user(self, user, url):
        t = self.topology_model.objects.first()
        self._create_org_user(user=user, organization=t.organization, is_admin=True)
        self.client.force_login(user)
        r = self.client.get(url)
        self.assertContains(
            r, "You do not have permission to perform this action.", status_code=403
        )

    def test_list_visualizer_with_auth_enabled(self):
        user = self._create_user(username="list-user", email="list@email.com")
        url = reverse("topology_list")

        with self.subTest("test list visualizer with not auth user"):
            self._test_visualizer_with_unauthenticated_user(url)

        with self.subTest("test list visualizer with not permitted user"):
            self._test_visualizer_with_not_permitted_user(user, url)

        with self.subTest("test list visualizer with not a manager user"):
            self._test_visualizer_with_not_a_manager_user(user, url)

    def test_detail_visualizer_with_auth_enabled(self):
        user = self._create_user(username="detail-user", email="detail@email.com")
        t = self.topology_model.objects.first()
        url = reverse("topology_detail", args=[t.pk])

        with self.subTest("test detail visualizer with not auth user"):
            self._test_visualizer_with_unauthenticated_user(url)

        with self.subTest("test detail visualizer with not permitted user"):
            self._test_visualizer_with_not_permitted_user(user, url)

        with self.subTest("test detail visualizer with not a manager user"):
            self._test_visualizer_with_not_a_manager_user(user, url, is_detail=True)

    def _successful_visualizer_tests(self):
        with self.subTest("test superuser on list visualizer"):
            r = self.client.get(reverse("topology_list"))
            self.assertContains(r, "TestNetwork")

        with self.subTest("test superuser on detail visualizer"):
            t = self.topology_model.objects.first()
            r = self.client.get(reverse("topology_detail", args=[t.pk]))
            self.assertContains(r, t.pk)

    def test_visualizer_with_auth_enabled_superuser(self):
        user = self._create_admin(username="super-visualizer", email="s@email.com")
        self.client.force_login(user)
        self._successful_visualizer_tests()

    @patch.object(app_settings, "TOPOLOGY_API_AUTH_REQUIRED", return_value=False)
    def test_visualizer_with_auth_disabled(self, mocked):
        self._successful_visualizer_tests()

    @patch.object(app_settings, "TOPOLOGY_API_AUTH_REQUIRED", return_value=False)
    def test_visualizer_with_auth_disabled_superuser(self, mocked):
        user = self._create_admin(username="super-visualizer", email="s@email.com")
        self.client.force_login(user)
        self._successful_visualizer_tests()
