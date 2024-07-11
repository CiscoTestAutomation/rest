#!/bin/env python
""" Unit tests for the rest.connector cisco-shared package. """
import os
import unittest
from requests.models import Response
from unittest.mock import patch, MagicMock

from pyats.topology import loader

from rest.connector import Rest
HERE = os.path.dirname(__file__)


class test_rest_connector(unittest.TestCase):
    def setUp(self):
        self.testbed = loader.load(os.path.join(HERE, 'testbed.yaml'))
        self.device = self.testbed.devices['ise']

    def test_init(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.device, self.device)

        with self.assertRaises(NotImplementedError):
            self.assertRaises(connection.execute())
        with self.assertRaises(NotImplementedError):
            self.assertRaises(connection.configure())

    def test_connection(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.session') as req:
            resp = Response()
            resp.headers['Content-type'] = 'application/json'
            resp.status_code = 200
            resp._content = b'{"OperationResult": {"resultValue": [{"value": "3.3.0.430",' + \
                            b' "name": "version"}, {"value": "0", "name": "patch information"}]}}'
            req().request.return_value = resp
            connection.connect()
            self.assertEqual(connection.connected, True)
            connection.connect()
            self.assertEqual(connection.connected, True)

        # Now disconnect
        with patch('requests.session') as req:
            connection.disconnect()
        self.assertEqual(connection.connected, False)

