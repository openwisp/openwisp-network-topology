SIMPLE_MESH_DATA = {
    '2a:9a:fb:12:11:77': [
        {
            'mac': '2a:9a:fb:12:11:77',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': False,
                        'mac': 'a4:bc:3f:ae:c7:0c',
                        'mfp': False,
                        'noise': -95,
                        'signal': -56,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -95,
                'signal': -64,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    '64:70:02:c3:03:b3': [
        {
            'mac': '64:70:02:c3:03:b3',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'a4:bc:3f:ae:c7:0c',
                        'mfp': False,
                        'noise': -95,
                        'signal': -54,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '2a:9a:fb:12:11:77',
                        'mfp': False,
                        'noise': -95,
                        'signal': -68,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -95,
                'signal': -61,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    'a4:bc:3f:ae:c7:0c': [
        {
            'mac': 'a4:bc:3f:ae:c7:0c',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '64:70:02:C3:03:B3',
                        'mfp': False,
                        'noise': -95,
                        'signal': -52,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '2a:9a:fb:12:11:77',
                        'mfp': False,
                        'noise': -95,
                        'signal': -61,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -95,
                'signal': -56,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
}

COMPLEX_MESH_DATA = {
    '35:7e:5a:98:8b:ee': [
        {
            'mac': '35:7e:5a:98:8b:ee',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd1:8a:80:8c:34:e2',
                        'mfp': False,
                        'noise': -92,
                        'signal': -22,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'a0:ed:b0:47:62:2c',
                        'mfp': False,
                        'noise': -92,
                        'signal': 12,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd0:42:39:14:4f:91',
                        'mfp': False,
                        'noise': -92,
                        'signal': 11,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': False,
                        'mac': 'fb:57:19:16:90:4d',
                        'mfp': False,
                        'noise': -92,
                        'signal': -4,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '20:8b:e1:05:6e:78',
                        'mfp': False,
                        'noise': -92,
                        'signal': -17,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'ed:10:af:18:76:6c',
                        'mfp': False,
                        'noise': -92,
                        'signal': -14,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -92,
                'signal': -5,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    'd0:42:39:14:4f:91': [
        {
            'mac': 'd0:42:39:14:4f:91',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'fb:57:19:16:90:4d',
                        'mfp': False,
                        'noise': -95,
                        'signal': -26,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'a0:ed:b0:47:62:2c',
                        'mfp': False,
                        'noise': -95,
                        'signal': -20,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '35:7e:5a:98:8b:ee',
                        'mfp': False,
                        'noise': -95,
                        'signal': -19,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd1:8a:80:8c:34:e2',
                        'mfp': False,
                        'noise': -95,
                        'signal': -21,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'ed:10:af:18:76:6c',
                        'mfp': False,
                        'noise': -95,
                        'signal': 10,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '20:8b:e1:05:6e:78',
                        'mfp': False,
                        'noise': -95,
                        'signal': -16,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -95,
                'signal': -6,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    '2a:9a:fb:12:11:77': [
        {
            'mac': '2a:9a:fb:12:11:77',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '64:70:02:C3:03:B3',
                        'mfp': False,
                        'noise': -95,
                        'signal': -73,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': False,
                        'mac': 'a4:bc:3f:ae:c7:0c',
                        'mfp': False,
                        'noise': -95,
                        'signal': -56,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -95,
                'signal': -64,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    '20:8b:e1:05:6e:78': [
        {
            'mac': '20:8b:e1:05:6e:78',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd1:8a:80:8c:34:e2',
                        'mfp': False,
                        'noise': -95,
                        'signal': -23,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'ed:10:af:18:76:6c',
                        'mfp': False,
                        'noise': -95,
                        'signal': -20,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'a0:ed:b0:47:62:2c',
                        'mfp': False,
                        'noise': -95,
                        'signal': 4,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '35:7e:5a:98:8b:ee',
                        'mfp': False,
                        'noise': -95,
                        'signal': 9,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'fb:57:19:16:90:4d',
                        'mfp': False,
                        'noise': -95,
                        'signal': -30,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd0:42:39:14:4f:91',
                        'mfp': False,
                        'noise': -95,
                        'signal': 6,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -95,
                'signal': -7,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    'ed:10:af:18:76:6c': [
        {
            'mac': 'ed:10:af:18:76:6c',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd1:8a:80:8c:34:e2',
                        'mfp': False,
                        'noise': -94,
                        'signal': 6,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'fb:57:19:16:90:4d',
                        'mfp': False,
                        'noise': -94,
                        'signal': 2,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'a0:ed:b0:47:62:2c',
                        'mfp': False,
                        'noise': -94,
                        'signal': 5,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd0:42:39:14:4f:91',
                        'mfp': False,
                        'noise': -94,
                        'signal': 10,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '35:7e:5a:98:8b:ee',
                        'mfp': False,
                        'noise': -94,
                        'signal': 7,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '20:8b:e1:05:6e:78',
                        'mfp': False,
                        'noise': -94,
                        'signal': -9,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -94,
                'signal': 1,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    'fb:57:19:16:90:4d': [
        {
            'mac': 'fb:57:19:16:90:4d',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'ed:10:af:18:76:6c',
                        'mfp': False,
                        'noise': -95,
                        'signal': 0,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd1:8a:80:8c:34:e2',
                        'mfp': False,
                        'noise': -95,
                        'signal': 5,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'a0:ed:b0:47:62:2c',
                        'mfp': False,
                        'noise': -95,
                        'signal': -2,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd0:42:39:14:4f:91',
                        'mfp': False,
                        'noise': -95,
                        'signal': -17,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '35:7e:5a:98:8b:ee',
                        'mfp': False,
                        'noise': -95,
                        'signal': -2,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '20:8b:e1:05:6e:78',
                        'mfp': False,
                        'noise': -95,
                        'signal': -1,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -95,
                'signal': -16,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    'a4:bc:3f:ae:c7:0c': [
        {
            'mac': 'a4:bc:3f:ae:c7:0c',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '64:70:02:C3:03:B3',
                        'mfp': False,
                        'noise': -95,
                        'signal': -52,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '2a:9a:fb:12:11:77',
                        'mfp': False,
                        'noise': -95,
                        'signal': -61,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -95,
                'signal': -56,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    '64:70:02:c3:03:b3': [
        {
            'mac': '64:70:02:c3:03:b3',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'a4:bc:3f:ae:c7:0c',
                        'mfp': False,
                        'noise': -95,
                        'signal': -54,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '2a:9a:fb:12:11:77',
                        'mfp': False,
                        'noise': -95,
                        'signal': -68,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -95,
                'signal': -61,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    'a0:ed:b0:47:62:2c': [
        {
            'mac': 'a0:ed:b0:47:62:2c',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': False,
                        'mac': 'ed:10:af:18:76:6c',
                        'mfp': False,
                        'noise': -94,
                        'signal': -2,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'fb:57:19:16:90:4d',
                        'mfp': False,
                        'noise': -94,
                        'signal': -6,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd1:8a:80:8c:34:e2',
                        'mfp': False,
                        'noise': -94,
                        'signal': 5,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd0:42:39:14:4f:91',
                        'mfp': False,
                        'noise': -94,
                        'signal': 7,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '35:7e:5a:98:8b:ee',
                        'mfp': False,
                        'noise': -94,
                        'signal': 4,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '20:8b:e1:05:6e:78',
                        'mfp': False,
                        'noise': -94,
                        'signal': 3,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -94,
                'signal': 1,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
    'd1:8a:80:8c:34:e2': [
        {
            'mac': 'd1:8a:80:8c:34:e2',
            'mtu': 1500,
            'multicast': True,
            'name': 'mesh0',
            'txqueuelen': 1000,
            'type': 'wireless',
            'up': True,
            'wireless': {
                'channel': 11,
                'clients': [
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'ed:10:af:18:76:6c',
                        'mfp': False,
                        'noise': -95,
                        'signal': 9,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'a0:ed:b0:47:62:2c',
                        'mfp': False,
                        'noise': -95,
                        'signal': 3,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'fb:57:19:16:90:4d',
                        'mfp': False,
                        'noise': -95,
                        'signal': 6,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': 'd0:42:39:14:4f:91',
                        'mfp': False,
                        'noise': -95,
                        'signal': 5,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '35:7e:5a:98:8b:ee',
                        'mfp': False,
                        'noise': -95,
                        'signal': 2,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                    {
                        'auth': True,
                        'authorized': True,
                        'ht': True,
                        'mac': '20:8b:e1:05:6e:78',
                        'mfp': False,
                        'noise': -95,
                        'signal': 1,
                        'vendor': 'TP-LINK ' 'TECHNOLOGIES ' 'CO.,LTD.',
                        'vht': False,
                        'wmm': True,
                    },
                ],
                'country': 'ES',
                'frequency': 2462,
                'htmode': 'HT20',
                'mode': '802.11s',
                'noise': -95,
                'signal': 0,
                'ssid': 'Test Mesh',
                'tx_power': 17,
            },
        }
    ],
}