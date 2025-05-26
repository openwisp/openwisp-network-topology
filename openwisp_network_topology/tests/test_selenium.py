from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from swapper import load_model

from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.tests import SeleniumTestMixin

from .utils import CreateGraphObjectsMixin, LoadMixin

Link = load_model("topology", "Link")
Node = load_model("topology", "Node")
Topology = load_model("topology", "Topology")


@tag("selenium_tests")
class TestTopologyGraphVisualizer(
    TestOrganizationMixin,
    CreateGraphObjectsMixin,
    LoadMixin,
    SeleniumTestMixin,
    StaticLiveServerTestCase,
):
    app_label = "topology"
    node_model = Node
    link_model = Link
    topology_model = Topology
    _EXPECTED_KEYS = ["Label", "Protocol", "Version", "Metric", "Nodes", "Links"]

    @property
    def prefix(self):
        return f"admin:{self.app_label}"

    def setUp(self):
        org = self._create_org()
        self.admin = self._create_admin(
            username=self.admin_username, password=self.admin_password
        )
        self.topology = self._create_topology(organization=org)
        self._create_node(
            label="node1",
            addresses=["192.168.0.1"],
            topology=self.topology,
            organization=org,
        )
        self._create_node(
            label="node2",
            addresses=["192.168.0.2"],
            topology=self.topology,
            organization=org,
        )

    def tearDown(self):
        # Clear the web driver console logs after each test
        self.get_browser_logs()

    def _assert_topology_graph(self, hide_loading_overlay=True):
        if hide_loading_overlay:
            self.hide_loading_overlay("loadingContainer")
        self.find_element(By.CLASS_NAME, "sideBarHandle").click()
        self.wait_for_visibility(By.CLASS_NAME, "njg-metaInfoContainer")
        self.wait_for_visibility(By.XPATH, "//div[1]/canvas")
        self.assertEqual(self.get_browser_logs(), [])
        topology_graph_dict = self.topology.json(dict=True)
        topology_graph_label_keys = self.find_elements(By.CSS_SELECTOR, ".njg-keyLabel")
        topology_graph_label_values = self.find_elements(
            By.CSS_SELECTOR, ".njg-valueLabel"
        )
        self.assertEqual(len(topology_graph_label_keys), len(self._EXPECTED_KEYS))
        # ensure correct topology graph labels are present
        for key in topology_graph_label_keys:
            self.assertIn(key.text, self._EXPECTED_KEYS)
        expected_label_values = [
            topology_graph_dict["label"],
            topology_graph_dict["protocol"],
            topology_graph_dict["version"],
            topology_graph_dict["metric"],
            str(len(topology_graph_dict["nodes"])),
            str(len(topology_graph_dict["links"])),
        ]
        for label_value, expected_value in zip(
            topology_graph_label_values, expected_label_values
        ):
            self.assertEqual(label_value.text, expected_value)

    def test_topology_admin_view_graph_visualizer(self):
        path = reverse(f"{self.prefix}_topology_change", args=[self.topology.pk])
        self.login()
        self.open(path)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        self._assert_topology_graph()

    def test_unpublished_topology_admin_view_graph_visualizer(self):
        self.topology_model.objects.update(published=False)
        path = reverse(f"{self.prefix}_topology_change", args=[self.topology.pk])
        self.login()
        self.open(path)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        self._assert_topology_graph()

    def test_topology_non_admin_view_graph_visualizer(self):
        self.login()
        self.open(reverse("topology_list"), html_container="body.frontend")
        self.find_element(By.XPATH, "//ul[@id='menu']/li/a").click()
        self._assert_topology_graph()

    def test_topology_admin_visualizer_multiple_close_btn_append(self):
        path = reverse(f"{self.prefix}_topology_change", args=[self.topology.pk])
        self.login()
        self.open(path)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        self._assert_topology_graph()
        self.find_element(By.CLASS_NAME, "closeBtn").click()
        # Now try to open visualizer
        # again and make sure only single
        # 'closeBtn' element is present in the DOM
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        self._assert_topology_graph()
        try:
            self.find_element(By.CLASS_NAME, "closeBtn").click()
        except ElementClickInterceptedException:
            self.fail('Multiple "closeBtn" are present in the visualizer DOM')

    def test_topology_admin_esc_key_close_visualizer(self):
        path = reverse(f"{self.prefix}_topology_change", args=[self.topology.pk])
        self.login()
        self.open(path)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        self._assert_topology_graph()
        # Try to close the visualizer with the "Esc" key.
        body = self.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ESCAPE)
        # Open the visualizer again and make sure no JS errors
        # are thrown when the visualizer is closed again
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        self._assert_topology_graph(hide_loading_overlay=False)
        self.find_element(By.CLASS_NAME, "closeBtn").click()
        console_logs = self.get_browser_logs()
        self.assertEqual(console_logs, [])
