#!/bin/env python
""" Unit tests for the NSO REST implementation """

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import unittest
from ipaddress import IPv6Address
import requests_mock

from pyats.topology import loader

from rest.connector import Rest

HERE = os.path.dirname(__file__)

def get_mock_server_address(testbed_device, connection_name):
    # Test for IPv6, set the mocker URL accordingly
    try:
        destination_host = testbed_device.connections[connection_name].host
    except AttributeError:
        destination_host = testbed_device.connections[connection_name].ip
        if isinstance(destination_host, IPv6Address):
            destination_host = f"[{IPv6Address(destination_host).exploded}]"
    return destination_host


@requests_mock.Mocker(kw='mock')
class test_nso_test_connector(unittest.TestCase):

    def setUp(self):
        self.testbed = loader.load(os.path.join(HERE, 'testbed.yaml'))
        self.device = self.testbed.devices['ncs']
        self.testbed_connection_names = ["rest", "rest-ipv6", "rest-fqdn"]

    def generate_connection(self, **kwargs):
        try:
            connection_name = kwargs["connection_name"]
        except KeyError:
            connection_name = "rest"

        connection = Rest(device=self.device, alias="rest", via=connection_name)

        response_text = """
        <api xmlns="http://tail-f.com/ns/rest" xmlns:y="http://tail-f.com/ns/rest">
          <version>0.5</version>
          <config/>
          <running/>
          <operational/>
          <operations/>
          <rollbacks/>
        </api>
        """

        # Set the mocker URL
        destination_host = get_mock_server_address(self.device, connection_name)
        kwargs['mock'].get(f'http://{destination_host}:8080/api', text=response_text)
        connection.connect(verbose=True)
        return connection

    def test_connect(self, **kwargs):
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                self.assertEqual(connection.connected, True)


    def test_get(self, **kwargs):

        response_text = """\
{
  "tailf-ncs:devices": {
    "global-settings": {
      "trace-dir": "./logs"
    },
    "authgroups": {
      "group": [
        {
          "name": "default"
        },
        {
          "name": "virl"
        }
      ],
      "snmp-group": [
        {
          "name": "default"
        }
      ]
    },
    "mib-group": [
      {
        "name": "snmp"
      }
    ],
    "device": [
      {
        "name": "R1"
      }
    ],
    "operations": {
      "connect": "/api/running/devices/_operations/connect",
      "sync-to": "/api/running/devices/_operations/sync-to",
      "sync-from": "/api/running/devices/_operations/sync-from",
      "disconnect": "/api/running/devices/_operations/disconnect",
      "check-sync": "/api/running/devices/_operations/check-sync",
      "check-yang-modules": "/api/running/devices/_operations/check-yang-modules",
      "fetch-ssh-host-keys": "/api/running/devices/_operations/fetch-ssh-host-keys",
      "clear-trace": "/api/running/devices/_operations/clear-trace"
    }
  }
}
"""
        url = "/api/running/devices"
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].get(f'http://{destination_host}:8080%s' % url, text=response_text)
                output = connection.get('/api/running/devices', verbose=True).text
                self.assertEqual(output, response_text)
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_post(self, **kwargs):

        response_text = """\
<output xmlns='http://tail-f.com/ns/ncs'>
  <result>in-sync</result>
</output>
"""
        url = '/api/running/devices/device/R1/_operations/check-sync'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].post(f'http://{destination_host}:8080%s' % url, text=response_text)
                output = connection.post(url, content_type='xml', verbose=True).text
                self.assertEqual(output, response_text)
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_post_dict_payload_without_content_type(self, **kwargs):

        payload = {'abc': 'def'}

        response_text = """\
<output xmlns='http://tail-f.com/ns/ncs'>
  <result>in-sync</result>
</output>
"""
        url = '/api/running/devices/device/R1/_operations/check-sync'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].post(f'http://{destination_host}:8080%s' % url, text=response_text)
                try:
                    output = connection.post(url, payload, verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)

    def test_post_dict_payload_with_json_content_type(self, **kwargs):

        payload = {'abc': 'def'}

        response_text = """\
<output xmlns='http://tail-f.com/ns/ncs'>
  <result>in-sync</result>
</output>
"""
        url = '/api/running/devices/device/R1/_operations/check-sync'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].post(f'http://{destination_host}:8080%s' % url, text=response_text)
                try:
                    output = connection.post(url, payload, content_type='json', verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_post_dict_payload_with_xml_content_type(self, **kwargs):

        payload = {'abc': 'def'}

        response_text = """\
<output xmlns='http://tail-f.com/ns/ncs'>
  <result>in-sync</result>
</output>
"""
        url = '/api/running/devices/device/R1/_operations/check-sync'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].post(f'http://{destination_host}:8080%s' % url, text=response_text)
                try:
                    output = connection.post(url, payload, content_type='xml', verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_patch(self, **kwargs):

        payload = """\
{
  "tailf-ned-cisco-ios:route": {
    "ip-route-forwarding-list": [
      {
        "prefix": "10.6.1.0",
        "mask": "255.255.255.0",
        "forwarding-address": "10.2.2.2"
      }
    ]
  }
}
"""
        url = '/api/running/devices/device/R1/config/ios:ip/route'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)

                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].patch(f'http://{destination_host}:8080%s' % url, status_code=204)
                output = connection.patch(url, payload, verbose=True).text
                self.assertEqual(output, '')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_patch_dict_payload_without_content_type(self, **kwargs):

        payload = {
          "tailf-ned-cisco-ios:route": {
            "ip-route-forwarding-list": [
              {
                "prefix": "10.6.1.0",
                "mask": "255.255.255.0",
                "forwarding-address": "10.2.2.2"
              }
            ]
          }
        }
        url = '/api/running/devices/device/R1/config/ios:ip/route'

        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].patch(f'http://{destination_host}:8080%s' % url, status_code=204)
                try:
                    output = connection.patch(url, payload, verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_patch_dict_payload_with_json_content_type(self, **kwargs):

        payload = {
          "tailf-ned-cisco-ios:route": {
            "ip-route-forwarding-list": [
              {
                "prefix": "10.6.1.0",
                "mask": "255.255.255.0",
                "forwarding-address": "10.2.2.2"
              }
            ]
          }
        }

        url = '/api/running/devices/device/R1/config/ios:ip/route'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].patch(f'http://{destination_host}:8080%s' % url, status_code=204)
                output = connection.patch(url, payload, content_type='json', verbose=True).text
                self.assertEqual(output, '')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_patch_dict_payload_with_xml_content_type(self, **kwargs):

        payload = {
          "tailf-ned-cisco-ios:route": {
            "ip-route-forwarding-list": [
              {
                "prefix": "10.6.1.0",
                "mask": "255.255.255.0",
                "forwarding-address": "10.2.2.2"
              }
            ]
          }
        }

        url = '/api/running/devices/device/R1/config/ios:ip/route'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].patch(f'http://{destination_host}:8080%s' % url, status_code=204)
                output = connection.patch(url, payload, content_type='xml', verbose=True).text
                self.assertEqual(output, '')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_put(self, **kwargs):

        payload = """\
{
  "tailf-ned-cisco-ios:route": {
    "ip-route-forwarding-list": [
      {
        "prefix": "10.1.1.0",
        "mask": "255.255.255.0",
        "forwarding-address": "10.2.2.2"
      },
      {
        "prefix": "10.2.1.0",
        "mask": "255.255.255.0",
        "forwarding-address": "10.2.2.2"
      }
    ]
  }
}
"""

        url = '/api/running/devices/device/R1/config/ios:ip/route'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].put(f'http://{destination_host}:8080%s' % url, status_code=204)
                output = connection.put(url, payload, verbose=True).text
                self.assertEqual(output, '')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_put_dict_payload_without_content_type(self, **kwargs):

        payload = {
          "tailf-ned-cisco-ios:route": {
            "ip-route-forwarding-list": [
              {
                "prefix": "10.1.1.0",
                "mask": "255.255.255.0",
                "forwarding-address": "10.2.2.2"
              },
              {
                "prefix": "10.2.1.0",
                "mask": "255.255.255.0",
                "forwarding-address": "10.2.2.2"
              }
            ]
          }
        }

        url = '/api/running/devices/device/R1/config/ios:ip/route'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].put(f'http://{destination_host}:8080%s' % url, status_code=204)
                try:
                    output = connection.put(url, payload, verbose=True).text
                except AssertionError as e:
                    self.assertEqual(str(e), 'content_type parameter required when passing dict')
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_put_dict_payload_with_json_content_type(self, **kwargs):

        payload = {
          "tailf-ned-cisco-ios:route": {
            "ip-route-forwarding-list": [
              {
                "prefix": "10.1.1.0",
                "mask": "255.255.255.0",
                "forwarding-address": "10.2.2.2"
              },
              {
                "prefix": "10.2.1.0",
                "mask": "255.255.255.0",
                "forwarding-address": "10.2.2.2"
              }
            ]
          }
        }

        url = '/api/running/devices/device/R1/config/ios:ip/route'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].put(f'http://{destination_host}:8080%s' % url, status_code=204)
                output = connection.put(url, payload, content_type='json', verbose=True).text
                connection.disconnect()

                self.assertEqual(connection.connected, False)


    def test_put_dict_payload_with_xml_content_type(self, **kwargs):

        payload = {
          "tailf-ned-cisco-ios:route": {
            "ip-route-forwarding-list": [
              {
                "prefix": "10.1.1.0",
                "mask": "255.255.255.0",
                "forwarding-address": "10.2.2.2"
              },
              {
                "prefix": "10.2.1.0",
                "mask": "255.255.255.0",
                "forwarding-address": "10.2.2.2"
              }
            ]
          }
        }

        url = '/api/running/devices/device/R1/config/ios:ip/route'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].put(f'http://{destination_host}:8080%s' % url, status_code=204)
                output = connection.put(url, payload, content_type='xml', verbose=True).text
                connection.disconnect()

                self.assertEqual(connection.connected, False)



    def test_delete(self, **kwargs):

        url = '/api/running/devices/device/R1/config/ios:ip/route'
        for connection_name in self.testbed_connection_names:
            with self.subTest(connection_name=connection_name):
                connection = self.generate_connection(connection_name=connection_name, **kwargs)
                destination_host = get_mock_server_address(self.device, connection_name)
                kwargs['mock'].delete(f'http://{destination_host}:8080%s' % url, status_code=204)
                output = connection.delete(url, verbose=True).text
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
