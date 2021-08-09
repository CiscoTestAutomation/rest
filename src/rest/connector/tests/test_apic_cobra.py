#!/bin/env python
""" Unit tests for APIC rest.connector """

import os
import unittest
from importlib import import_module

import requests
from requests.models import Response
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError

from pyats.topology import loader

from rest.connector import Acisdk
from rest.connector.utils import get_installed_lib_versions
HERE = os.path.dirname(__file__)


class test_rest_connector(unittest.TestCase):

    def setUp(self):
        self.testbed = loader.load(os.path.join(HERE, 'testbed.yaml'))
        self.device = self.testbed.devices['apic']

        libs = get_installed_lib_versions()
        if not all(libs.values()) or len(set(libs.values())) != 1:
            # both libraries should be already installed and have the same version
            self.libs_present = False
        else:
            self.sdk_version = list(libs.values())[0]
            self.libs_present = True

    def test_init(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req().return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')
            self.assertEqual(connection.device, self.device)

        with self.assertRaises(NotImplementedError):
            self.assertRaises(connection.execute())
        with self.assertRaises(NotImplementedError):
            self.assertRaises(connection.configure())

    def test_connection(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req.return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')
            self.assertEqual(connection.connected, False)

        with patch('requests.post') as req:
            resp = Response()
            resp.status_code = 200
            resp.json = MagicMock(return_value={'imdata': [{'aaaLogin': {
                'attributes': {'token': 'test',
                               'version': 'test',
                               'refreshTimeoutSeconds': 600
                               }
            }}]})
            req.return_value = resp
            connection.connect()
            self.assertEqual(connection.connected, True)
            connection.connect()
            self.assertEqual(connection.connected, True)

        # Now disconnect
        with patch('requests.post') as req:
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_connection_wrong_code(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req.return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')
        self.assertEqual(connection.connected, False)

        with patch('requests.post') as req:
            resp = Response()
            resp.status_code = 404
            req.return_value = resp
            with self.assertRaises(HTTPError):
                connection.connect()

        self.assertEqual(connection.connected, False)

        # Now disconnect
        with patch('requests.post') as req:
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_attribute_call_not_connected(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req.return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')
        with self.assertRaises(Exception):
            connection.lookupByDn('uni')

    def test_attribute_call_connected(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req.return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')
            self.assertEqual(connection.connected, False)

            with patch('requests.post') as req, patch('requests.Session') as session:
                resp = Response()
                resp.status_code = 200
                resp.json = MagicMock(return_value={'imdata': [{'aaaLogin': {
                    'attributes': {'token': 'test',
                                   'version': 'test',
                                   'refreshTimeoutSeconds': 600
                                   }
                }}]})
                req.return_value = resp
                connection.connect()

                resp._content = str.encode('<?xml version="1.0" ?><imdata totalCount="0"></imdata>')
                session().get.return_value = resp
                mo = connection.create(model='fv.Tenant',
                                       parent_mo_or_dn='uni',
                                       name='test')
                connection.lookupByDn('uni')
                connection.disconnect()
            self.assertEqual(connection.connected, False)

    def test_get_model_wrong_model_format(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req.return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')

        with self.assertRaises(NameError):
            connection.get_model(model='wrong_model')

    def test_get_model_wrong_model(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req.return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')

        with self.assertRaises(AttributeError):
            connection.get_model(model='fv.Wrong')

    def test_get_model(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        '''
        get_model is not dependant on connection,
        as it leverages the locally installed libraries
        '''
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req.return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')
        self.assertEqual(connection.connected, False)

        model = connection.get_model(model='fv.Tenant')
        tenant_model = getattr(import_module(f'cobra.model.fv'), 'Tenant')
        self.assertEqual(model, tenant_model)

    def test_config_and_commit_not_connected(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req.return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')
        self.assertEqual(connection.connected, False)
        with self.assertRaises(Exception):
            mo = connection.create(model='fv.Tenant',
                                   parent_mo_or_dn='uni',
                                   name='test')

            connection.config_and_commit(mo=mo)

    def test_config_and_commit_connected(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req.return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')
        self.assertEqual(connection.connected, False)

        with patch('requests.post') as req, patch('requests.Session') as session:
            resp = Response()
            resp.status_code = 200
            resp.json = MagicMock(return_value={'imdata': [{'aaaLogin': {
                'attributes': {'token': 'test',
                               'version': 'test',
                               'refreshTimeoutSeconds': 600
                               }
            }}]})
            req.return_value = resp
            connection.connect()

            resp.json = MagicMock(return_value={'imdata': []})
            session().post.return_value = resp
            mo = connection.create(model='fv.Tenant',
                                   parent_mo_or_dn='uni',
                                   name='test')
            connection.config_and_commit(mo=mo)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_config_and_commit_connected_wrong_status(self):
        if not self.libs_present:
            self.skipTest('Test skipped due to missing libraries')
        with patch('requests.get') as req:
            resp = Response()
            resp.status_code = 200
            resp._content = str.encode('<title>Cisco APIC Python SDK Documentation &#8212; Cisco APIC '
                                       f'Python API {self.sdk_version} documentation</title>')
            req.return_value = resp
            connection = Acisdk(device=self.device, alias='cobra', via='cobra')
        self.assertEqual(connection.connected, False)

        with patch('requests.post') as req, patch('requests.Session') as session:
            resp = Response()
            resp.status_code = 200
            resp.json = MagicMock(return_value={'imdata': [{'aaaLogin': {
                'attributes': {'token': 'test',
                               'version': 'test',
                               'refreshTimeoutSeconds': 600
                               }
            }}]})
            req.return_value = resp
            connection.connect()

            resp2 = Response()
            resp2.status_code = 300
            session().post.return_value = resp2

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            with self.assertRaises(Exception):
                mo = connection.create(model='fv.Tenant',
                                       parent_mo_or_dn='uni',
                                       name='test')
                connection.config_and_commit(mo=mo)
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)


if __name__ == '__main__':
    unittest.main()
