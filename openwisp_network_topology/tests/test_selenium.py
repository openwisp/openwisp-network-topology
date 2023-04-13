from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from openwisp_controller.tests.utils import SeleniumTestMixin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from swapper import load_model

from openwisp_users.tests.utils import TestOrganizationMixin

from .utils import CreateGraphObjectsMixin, LoadMixin

Link = load_model('topology', 'Link')
Node = load_model('topology', 'Node')
Topology = load_model('topology', 'Topology')


class TestTopologyGraphVisualizer(
    TestOrganizationMixin,
    CreateGraphObjectsMixin,
    LoadMixin,
    SeleniumTestMixin,
    StaticLiveServerTestCase,
):
    app_label = 'topology'
    admin_username = 'admin'
    admin_password = 'password'
    node_model = Node
    link_model = Link
    topology_model = Topology
    _EXPECTED_KEYS = ['Label', 'Protocol', 'Version', 'Metric', 'Nodes', 'Links']

    @property
    def prefix(self):
        return f'admin:{self.app_label}'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = webdriver.ChromeOptions()
        if getattr(settings, 'SELENIUM_HEADLESS', True):
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1366,768')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--remote-debugging-port=9222')
        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}
        cls.web_driver = webdriver.Chrome(
            options=chrome_options, desired_capabilities=capabilities
        )

    @classmethod
    def tearDownClass(cls):
        cls.web_driver.quit()
        super().tearDownClass()

    def setUp(self):
        org = self._create_org()
        self.admin = self._create_admin(
            username=self.admin_username, password=self.admin_password
        )
        self.topology = self._create_topology(organization=org)
        self._create_node(
            label='node1',
            addresses=['192.168.0.1'],
            topology=self.topology,
            organization=org,
        )
        self._create_node(
            label='node2',
            addresses=['192.168.0.2'],
            topology=self.topology,
            organization=org,
        )

    def tearDown(self):
        # Clear the web driver console logs after each test
        self.web_driver.get_log('browser')

    def _get_console_errors(self, console_logs=[]):
        console_errors = []
        exclude_socket_icon_errors = [
            'WebSocket handshake',
            'favicon.ico - Failed to load resource:',
        ]
        for log in console_logs:
            error_message = log['message']
            error_level = log['level']
            if error_level == 'SEVERE' and any(
                [err in error_message for err in exclude_socket_icon_errors]
            ):
                continue
            console_errors.append(log)
        return console_errors

    def _assert_topology_graph(self):
        WebDriverWait(self.web_driver, 2).until(
            EC.invisibility_of_element_located((By.ID, 'loadingContainer'))
        )
        sidebar = WebDriverWait(self.web_driver, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'sideBarHandle'))
        )
        sidebar.click()
        WebDriverWait(self.web_driver, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'njg-aboutContainer'))
        )
        topology_graph_label_keys = self.web_driver.find_elements_by_css_selector(
            '.njg-keyLabel'
        )
        topology_graph_label_values = self.web_driver.find_elements_by_css_selector(
            '.njg-valueLabel'
        )
        console_logs = self.web_driver.get_log('browser')
        console_errors = self._get_console_errors(console_logs)
        self.assertEqual(console_errors, [])
        topology_graph_dict = self.topology.json(dict=True)
        topology_graph_label_keys = self.web_driver.find_elements_by_css_selector(
            '.njg-keyLabel'
        )
        topology_graph_label_values = self.web_driver.find_elements_by_css_selector(
            '.njg-valueLabel'
        )
        self.assertEqual(len(topology_graph_label_keys), len(self._EXPECTED_KEYS))
        # ensure correct topology graph labels are present
        for key in topology_graph_label_keys:
            self.assertIn(key.text, self._EXPECTED_KEYS)
        expected_label_values = [
            topology_graph_dict['label'],
            topology_graph_dict['protocol'],
            topology_graph_dict['version'],
            topology_graph_dict['metric'],
            str(len(topology_graph_dict['nodes'])),
            str(len(topology_graph_dict['links'])),
        ]
        for label_value, expected_value in zip(
            topology_graph_label_values, expected_label_values
        ):
            self.assertEqual(label_value.text, expected_value)

    def test_topology_admin_view_graph_visualizer(self):
        path = reverse(f'{self.prefix}_topology_change', args=[self.topology.pk])
        self.login(username=self.admin_username, password=self.admin_password)
        self.open(path)
        self.web_driver.find_element_by_css_selector('input.visualizelink').click()
        self._assert_topology_graph()

    def test_topology_non_admin_view_graph_visualizer(self):
        path = reverse('topology_list')
        self.login(username=self.admin_username, password=self.admin_password)
        self.open(path)
        topology_graph_element = self.web_driver.find_element_by_xpath(
            "//ul[@id='menu']/li/a"
        )
        topology_graph_element.click()
        self._assert_topology_graph()
