#!/bin/env python
""" Unit tests for the IOS-XE REST implementation """

__copyright__ = "# Copyright (c) 2019 by cisco Systems, Inc. All rights reserved."
__author__ = "Maaz Mashood Mohiuddin <mmashood@cisco.com>"

import unittest
import json

from urllib.parse import urljoin
import requests_mock

from requests import RequestException

from rest.connector import Rest
from rest.connector.tests.utils import (generate_mock_server_url,
                                        get_testbed,
                                        return_all_request_data_from_mocker)

from .fixtures import (TEST_PAYLOAD_DICT,
                       TEST_PAYLOAD_JSON,
                       TEST_PAYLOAD_XML)


@requests_mock.Mocker(kw='mock')
class test_iosxe_test_connector(unittest.TestCase):

    def setUp(self):
        self.testbed = get_testbed()
        self.device = self.testbed.devices['eWLC']
        self.testbed_connection_names = ["rest", "rest-ipv6", "rest-fqdn"]

    def generate_connection(self, **kwargs):
        try:
            connection_name = kwargs["connection_name"]
        except KeyError:
            connection_name = "rest"

        connection = Rest(device=self.device, alias="rest", via=connection_name)

        response_text = """{
            "Cisco-IOS-XE-native:version": "17.3"
        }
        """

        # Set the mocker URL
        mocker_url = generate_mock_server_url(self.device, connection_name)
        login_url = urljoin(mocker_url, "/restconf/data/Cisco-IOS-XE-native:native/version")
        kwargs['mock'].get(login_url, text=response_text)
        connection.connect(verbose=True)
        return connection

    def test_connect(self, **kwargs):
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                self.assertEqual(connection.connected, True)


    def test_get(self, **kwargs):
        response_text = TEST_PAYLOAD_JSON

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile"
                kwargs['mock'].get(urljoin(mocker_url, restconf_path), text=response_text)

                output = connection.get(restconf_path, verbose=True).text
                self.assertEqual(output, response_text)

                connection.disconnect()
                self.assertEqual(connection.connected, False)

    def test_post(self, **kwargs):
        payload = TEST_PAYLOAD_DICT

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles"
                kwargs['mock'].post(urljoin(mocker_url, restconf_path), status_code=204)

                output = connection.post(restconf_path, payload, content_type='json', verbose=True).text
                self.assertEqual(output, '')

                connection.disconnect()
                self.assertEqual(connection.connected, False)


    def test_post_xml_payload_without_content_type(self, **kwargs):
        """
        Send an XML payload with the implementation default content-type (JSON)
        should result in a server returning a 400-series which should be
        caught by the response hook.
        """
        payload = TEST_PAYLOAD_DICT

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles"
                kwargs['mock'].post(urljoin(mocker_url, restconf_path), status_code=400)

                with self.assertRaises(RequestException):
                    connection.post(restconf_path, payload, verbose=True, content_type=None).text

                connection.disconnect()
                self.assertEqual(connection.connected, False)

    def test_post_dict_payload_with_json_content_type(self, **kwargs):
        """
        Default content-type is JSON, so a successful response should be
        returned
        """
        payload = TEST_PAYLOAD_DICT

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles"
                kwargs['mock'].post(urljoin(mocker_url, restconf_path), status_code=204)

                output = connection.post(restconf_path, payload, content_type='json', verbose=True).text
                self.assertEqual(output, '')

                connection.disconnect()
                self.assertEqual(connection.connected, False)

    def test_post_dict_payload_with_xml_content_type(self, **kwargs):

        payload = TEST_PAYLOAD_DICT
        expected_response = TEST_PAYLOAD_XML

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles"
                kwargs['mock'].post(urljoin(mocker_url, restconf_path), text=return_all_request_data_from_mocker)

                output = connection.post(restconf_path, payload, content_type='xml', verbose=True).json()
                self.assertEqual(output.get("body"), expected_response)

                connection.disconnect()
                self.assertEqual(connection.connected, False)


    def test_patch(self, **kwargs):

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

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile"
                kwargs['mock'].patch(urljoin(mocker_url, restconf_path), status_code=204)
                output = connection.patch(restconf_path, payload, content_type='json', verbose=True).text
                self.assertEqual(output, '')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_patch_dict_payload_without_content_type(self, **kwargs):

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

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile"
                kwargs['mock'].patch(urljoin(mocker_url, restconf_path), text=response_text)
                try:
                    output = connection.patch(restconf_path, payload, verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)

    def test_patch_dict_payload_with_json_content_type(self, **kwargs):

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

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile"

                kwargs['mock'].patch(urljoin(mocker_url, restconf_path), status_code=204)
                try:
                    output = connection.patch(restconf_path, payload, content_type='json', verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)

    def test_patch_dict_payload_with_xml_content_type(self, **kwargs):

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

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile"

                kwargs['mock'].patch(urljoin(mocker_url, restconf_path), status_code=204)
                try:
                    output = connection.patch(restconf_path, payload, content_type='xml', verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_put(self, **kwargs):

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

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles"

                kwargs['mock'].put(urljoin(mocker_url, restconf_path), status_code=204)
                output = connection.put(restconf_path, payload, content_type='json', verbose=True).text
                self.assertEqual(output, '')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_put_dict_payload_without_content_type(self, **kwargs):

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

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles"

                kwargs['mock'].put(urljoin(mocker_url, restconf_path), text=response_text, status_code=204)
                try:
                    output = connection.put(restconf_path, payload, verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)

    def test_put_dict_payload_with_json_content_type(self, **kwargs):

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

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles"

                kwargs['mock'].put(urljoin(mocker_url, restconf_path), status_code=204)
                try:
                    output = connection.put(restconf_path, payload, content_type='json', verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)

    def test_put_dict_payload_with_xml_content_type(self, **kwargs):

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

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles"

                kwargs['mock'].put(urljoin(mocker_url, restconf_path), status_code=204)
                try:
                    output = connection.put(restconf_path, payload, content_type='xml', verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_delete(self, **kwargs):
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                # Set the mocker URL
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=test-profile"

                kwargs['mock'].delete(urljoin(mocker_url, restconf_path), status_code=204)
                output = connection.delete(restconf_path, verbose=True).text
                self.assertEqual(output, '')
                connection.disconnect()

                self.assertEqual(connection.connected, False)

    def test_response_hook_raises_exception(self, **kwargs):
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=test-profile"

                kwargs['mock'].get(urljoin(mocker_url, restconf_path), status_code=401)
                with self.assertRaises(RequestException):
                    connection.get(restconf_path, verbose=True, timeout=1)

    def test_additional_headers(self, **kwargs):
        def return_client_headers(request, context):
            """
            Return all received headers to the client in the response body.
            """
            context.status_code = 200
            return json.dumps(dict(request.headers))

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                mocker_url = generate_mock_server_url(self.device, connection_name)
                restconf_path = "/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=test-profile"
                extra_headers = {"X-NEW-HEADER": "rest-testing"}

                kwargs['mock'].get(urljoin(mocker_url, restconf_path), text=return_client_headers)

                response = connection.get(restconf_path, verbose=True, timeout=1, headers=extra_headers)

                # Is the authorization header present in the response?
                self.assertEqual(response.request.headers["Authorization"],
                                 response.json().get("Authorization"),
                                 "Authorization header missing from response")

                self.assertEqual(response.request.headers["X-NEW-HEADER"],
                                 response.json().get("X-NEW-HEADER"),
                                 "Extra header missing from response")


                self.assertEqual(response.request.headers,
                                 response.json(),
                                 "Returned headers do not match sent.\n"
                                 "Expected: {response.request.headers}\n"
                                 "Received: {response.json()}")


if __name__ == "__main__":
    import sys
    import logging

    logging.basicConfig(stream=sys.stderr, level=logging.WARNING, format="%(asctime)s [%(levelname)8s]:  %(message)s")
    logger = logging.getLogger('rest')
    logger.setLevel(logging.DEBUG)
    unittest.main()
