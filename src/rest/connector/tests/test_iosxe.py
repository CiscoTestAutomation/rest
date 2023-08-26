#!/bin/env python
""" Unit tests for the IOS-XE REST implementation """

__copyright__ = "# Copyright (c) 2019 by cisco Systems, Inc. All rights reserved."
__author__ = "Maaz Mashood Mohiuddin <mmashood@cisco.com>"

import os
import unittest
import requests_mock

from pyats.topology import loader

from rest.connector import Rest

HERE = os.path.dirname(__file__)

@requests_mock.Mocker(kw='mock')
class test_iosxe_test_connector(unittest.TestCase):
# @requests_mock.Mocker(kw='mock')
# class test_iosxe_test_connector():

    def setUp(self):
        self.testbed = loader.load(os.path.join(HERE, 'testbed.yaml'))
        self.device = self.testbed.devices['eWLC']

    def test_connect(self, **kwargs):
        connection = Rest(device=self.device, alias='rest', via='rest')
        response_text = """{
            "Cisco-IOS-XE-native:version": "17.3"
        }
        """
        kwargs['mock'].get('https://198.51.100.3:443/restconf/data/Cisco-IOS-XE-native:native/version', text=response_text)
        output = connection.connect(verbose=True).text
        self.assertEqual(output, response_text)
        return connection

    def test_get(self, **kwargs):
        connection = self.test_connect()

        response_text = """{
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": [
        {
            "profile-name": "default-ap-profile",
            "description": "default ap profile",
            "hyperlocation": {
                "pak-rssi-threshold-detection": -50
            },
            "halo-ble-entries": {
                "halo-ble-entry": [
                    {
                        "beacon-id": 0
                    },
                    {
                        "beacon-id": 1
                    },
                    {
                        "beacon-id": 2
                    },
                    {
                        "beacon-id": 3
                    },
                    {
                        "beacon-id": 4
                    }
                ]
            }
        }
    ]
}
"""

        kwargs['mock'].get('https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile', text=response_text)
        output = connection.get('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile', verbose=True).text
        self.assertEqual(output, response_text)
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_post(self, **kwargs):
        connection = self.test_connect()

        payload = """
        {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": true,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
"""
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].post(url, status_code=204)
        output = connection.post('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='json', verbose=True).text
        self.assertEqual(output, '')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_post_dict_payload_without_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        response_text = ""

        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].post(url, text=response_text)
        try:
            output = connection.post('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_post_dict_payload_with_json_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].post(url, status_code=204)
        try:
            output = connection.post('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='json', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_post_dict_payload_with_xml_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].post(url, status_code=204)
        try:
            output = connection.post('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='xml', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_patch(self, **kwargs):
        connection = self.test_connect()

        payload = """{
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "hyperlocation": {
            "hyperlocation-enable": true,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
"""
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile'
        kwargs['mock'].patch(url, status_code=204)
        output = connection.patch('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile', payload, content_type='json', verbose=True).text
        self.assertEqual(output, '')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_patch_dict_payload_without_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        response_text = ""

        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile'
        kwargs['mock'].patch(url, text=response_text)
        try:
            output = connection.patch('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile', payload, verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_patch_dict_payload_with_json_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile'
        kwargs['mock'].patch(url, status_code=204)
        try:
            output = connection.patch('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile', payload, content_type='json', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_patch_dict_payload_with_xml_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile'
        kwargs['mock'].patch(url, status_code=204)
        try:
            output = connection.patch('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile', payload, content_type='xml', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_put(self, **kwargs):
        connection = self.test_connect()

        payload = """{
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": true,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
"""
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].put(url, status_code=204)
        output = connection.put('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='json', verbose=True).text
        self.assertEqual(output, '')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_put_dict_payload_without_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        response_text = ""

        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].put(url, text=response_text)
        try:
            output = connection.put('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_put_dict_payload_with_json_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].put(url, status_code=204)
        try:
            output = connection.put('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='json', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_put_dict_payload_with_xml_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].put(url, status_code=204)
        try:
            output = connection.put('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='xml', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_delete(self, **kwargs):
        connection = self.test_connect()

        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=test-profile'
        kwargs['mock'].delete(url, status_code=204)
        output = connection.delete('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=test-profile', verbose=True).text
        self.assertEqual(output, '')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


if __name__ == "__main__":
    import sys
    import logging

    logging.basicConfig(stream=sys.stderr, level=logging.WARNING, format="%(asctime)s [%(levelname)8s]:  %(message)s")
    logger = logging.getLogger('rest')
    logger.setLevel(logging.DEBUG)
    unittest.main()