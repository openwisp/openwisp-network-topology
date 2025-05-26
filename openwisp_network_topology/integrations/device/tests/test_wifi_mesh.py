import json
from copy import deepcopy
from unittest.mock import patch

import swapper
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.test import TransactionTestCase, tag
from django.urls import reverse
from django.utils.timezone import now, timedelta
from freezegun import freeze_time

from .. import settings as app_settings
from ..tasks import create_mesh_topology
from . import SIMPLE_MESH_DATA, SINGLE_NODE_MESH_DATA
from .utils import TopologyTestMixin

Node = swapper.load_model("topology", "Node")
Link = swapper.load_model("topology", "Link")
Topology = swapper.load_model("topology", "Topology")
DeviceNode = swapper.load_model("topology_device", "DeviceNode")
WifiMesh = swapper.load_model("topology_device", "WifiMesh")
Device = swapper.load_model("config", "Device")


@tag("wifi_mesh")
class TestWifiMeshIntegration(TopologyTestMixin, TransactionTestCase):
    app_label = "topology"

    def setUp(self):
        super().setUp()
        cache.clear()

    @property
    def prefix(self):
        return "admin:{0}".format(self.app_label)

    def _populate_mesh(self, data):
        org = self._get_org()
        devices = []
        for mac, interfaces in data.items():
            device = self._create_device(name=mac, mac_address=mac, organization=org)
            devices.append(device)
            response = self.client.post(
                "{0}?key={1}&time={2}".format(
                    reverse("monitoring:api_device_metric", args=[device.id]),
                    device.key,
                    now().utcnow().strftime("%d-%m-%Y_%H:%M:%S.%f"),
                ),
                data=json.dumps(
                    {
                        "type": "DeviceMonitoring",
                        "interfaces": interfaces,
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)
        create_mesh_topology.delay(organization_ids=(org.id,))
        return devices, org

    @patch.object(app_settings, "WIFI_MESH_INTEGRATION", False)
    def test_wifi_mesh_integration_disabled(self):
        with self.subTest('Test calling "create_mesh_topology" task'):
            with patch.object(WifiMesh, "create_topology") as mocked:
                _, org = self._populate_mesh(SIMPLE_MESH_DATA)
                self.assertEqual(Topology.objects.count(), 0)
                mocked.assert_not_called()

        # Ensure the following sub-test does not fail if the
        # previous one fails.
        Topology.objects.all().delete()

        with self.subTest("Test calling WifiMesh.create_topology"):
            with self.assertRaises(ImproperlyConfigured) as error:
                WifiMesh.create_topology(
                    organization_ids=[org.id], discard_older_data_time=360
                )
            self.assertEqual(
                str(error.exception),
                '"OPENIWSP_NETWORK_TOPOLOGY_WIFI_MESH_INTEGRATION" is set to "False".',
            )

    def test_simple_mesh(self):
        devices, org = self._populate_mesh(SIMPLE_MESH_DATA)
        self.assertEqual(Topology.objects.filter(organization=org).count(), 1)
        topology = Topology.objects.filter(organization=org).first()
        self.assertEqual(
            WifiMesh.objects.filter(topology=topology, mesh_id="Test Mesh@11").count(),
            1,
        )
        self.assertEqual(
            Node.objects.filter(
                topology=topology,
                organization=org,
                properties__contains=(
                    '{\n    "ht": true,\n    "vht": null,\n    "mfp": false,\n'
                    '    "wmm": true,\n    "vendor": "TP-LINK TECHNOLOGIES CO.,LTD."\n}'
                ),
            ).count(),
            3,
        )
        self.assertEqual(
            Link.objects.filter(
                topology=topology,
                organization=org,
                properties__contains='"noise": -94',
            )
            .filter(properties__contains='"signal": -58')
            .filter(properties__contains='"mesh_llid": 19500')
            .filter(properties__contains='"mesh_plid": 24500')
            .count(),
            3,
        )
        self.assertEqual(
            Link.objects.filter(
                topology=topology,
                organization=org,
                properties__contains='"mesh_non_peer_ps": "INCONSISTENT: (LISTEN / ACTIVE)"',
            ).count(),
            1,
        )
        self.assertEqual(DeviceNode.objects.filter(device__in=devices).count(), 3)

        # Test DeviceNode creation logic is not executed when the create_topology
        # is executed again
        with patch.object(DeviceNode, "auto_create") as mocked_auto_create:
            create_mesh_topology.delay(organization_ids=(org.id,))
            mocked_auto_create.assert_not_called()

    @patch("logging.Logger.exception")
    def test_single_node_mesh(self, mocked_logger):
        devices, org = self._populate_mesh(SINGLE_NODE_MESH_DATA)
        self.assertEqual(Topology.objects.filter(organization=org).count(), 1)
        topology = Topology.objects.filter(organization=org).first()
        self.assertEqual(
            WifiMesh.objects.filter(topology=topology, mesh_id="Test Mesh@11").count(),
            1,
        )
        self.assertEqual(
            Node.objects.filter(
                topology=topology,
                organization=org,
            ).count(),
            1,
        )
        self.assertEqual(
            Link.objects.filter(
                topology=topology,
                organization=org,
            ).count(),
            0,
        )
        self.assertEqual(DeviceNode.objects.filter(device__in=devices).count(), 1)
        mocked_logger.assert_not_called()

    def test_mesh_id_changed(self):
        devices, org = self._populate_mesh(SIMPLE_MESH_DATA)
        self.assertEqual(Topology.objects.filter(organization=org).count(), 1)
        self.assertEqual(WifiMesh.objects.filter(mesh_id="Test Mesh@11").count(), 1)
        topology = Topology.objects.filter(organization=org).first()
        self.assertEqual(
            Node.objects.filter(
                topology=topology,
                organization=org,
            ).count(),
            3,
        )
        self.assertEqual(
            Link.objects.filter(
                topology=topology,
                organization=org,
            ).count(),
            3,
        )
        # Change mesh_id reported in the monitoring data
        mesh_data = deepcopy(SIMPLE_MESH_DATA)
        for device, interfaces in zip(devices, mesh_data.values()):
            interfaces[0]["wireless"]["ssid"] = "New Mesh"
            response = self.client.post(
                "{0}?key={1}&time={2}".format(
                    reverse("monitoring:api_device_metric", args=[device.id]),
                    device.key,
                    now().utcnow().strftime("%d-%m-%Y_%H:%M:%S.%f"),
                ),
                data=json.dumps(
                    {
                        "type": "DeviceMonitoring",
                        "interfaces": interfaces,
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)
        create_mesh_topology.delay(organization_ids=(org.id,))
        self.assertEqual(Topology.objects.filter(organization=org).count(), 2)
        self.assertEqual(WifiMesh.objects.count(), 2)
        self.assertEqual(Node.objects.count(), 6)
        self.assertEqual(Link.objects.count(), 6)
        self.assertEqual(WifiMesh.objects.filter(mesh_id="New Mesh@11").count(), 1)
        topology = Topology.objects.filter(
            organization=org, wifimesh__mesh_id="New Mesh@11"
        ).first()
        self.assertEqual(
            Node.objects.filter(
                topology=topology,
                organization=org,
            ).count(),
            3,
        )
        self.assertEqual(
            Link.objects.filter(
                topology=topology,
                organization=org,
            ).count(),
            3,
        )

    def test_discard_old_monitoring_data(self):
        now_time = now()
        with freeze_time(now_time - timedelta(minutes=20)):
            devices, org = self._populate_mesh(SIMPLE_MESH_DATA)
        self.assertEqual(Topology.objects.count(), 1)
        topology = Topology.objects.first()
        self.assertEqual(topology.node_set.count(), 3)
        self.assertEqual(topology.link_set.filter(status="up").count(), 3)

        with freeze_time(now_time - timedelta(minutes=10)):
            # Only two devices sent monitoring data
            for device in devices[:2]:
                response = self.client.post(
                    "{0}?key={1}&time={2}".format(
                        reverse("monitoring:api_device_metric", args=[device.id]),
                        device.key,
                        now().utcnow().strftime("%d-%m-%Y_%H:%M:%S.%f"),
                    ),
                    data=json.dumps(
                        {
                            "type": "DeviceMonitoring",
                            "interfaces": SIMPLE_MESH_DATA[device.mac_address],
                        }
                    ),
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, 200)
            create_mesh_topology.delay(organization_ids=(org.id,))
        self.assertEqual(Topology.objects.count(), 1)
        self.assertEqual(topology.node_set.count(), 3)
        self.assertEqual(topology.link_set.filter(status="up").count(), 1)

        # No device is sending monitoring data
        create_mesh_topology.delay(organization_ids=(org.id,))
        self.assertEqual(Topology.objects.count(), 1)
        self.assertEqual(topology.node_set.count(), 3)
        self.assertEqual(topology.link_set.filter(status="up").count(), 0)

    def test_topology_admin(self):
        """
        Tests WifiMeshInlineAdmin is present in TopologyAdmin
        when OPENWISP_NETWORK_TOPOLOGY_WIFI_MESH_INTEGRATION
        is set to True.

        Note: This test is present here because TopologyAdmin class
        cannot be patched based on app_settings.WIFI_MESH_INTEGRATION
        once the project is initialized.
        """
        admin = self._create_admin()
        self.client.force_login(admin)

        with self.subTest("Test add form"):
            response = self.client.get(reverse(f"{self.prefix}_topology_add"))
            self.assertContains(response, "Wifi mesh")

        with self.subTest("Test change form"):
            topology = self._create_topology()
            response = self.client.get(
                reverse(f"{self.prefix}_topology_change", args=[topology.id])
            )
            self.assertContains(response, "Wifi mesh")
