#!/bin/env python
""" Unit tests for viptela/vManage rest.connector """

import os
import unittest
from requests.models import Response
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException

from pyats.topology import loader

from rest.connector import Rest
HERE = os.path.dirname(__file__)


class test_rest_connector(unittest.TestCase):

    def setUp(self):
        self.testbed = loader.load(os.path.join(HERE, 'testbed.yaml'))
        self.device = self.testbed.devices['vmanage']

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
            resp.status_code = 200
            req().post.return_value = resp
            req().get.return_value = resp
            connection.connect()
            self.assertEqual(connection.connected, True)
            connection.connect()
            self.assertEqual(connection.connected, True)

        # Now disconnect
        with patch('requests.session') as req:
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_post_not_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        with self.assertRaises(Exception):
            connection.post(mount_point='temp',
                            payload={'payload': 'something'})

    def test_connection_wrong_code(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.session') as req:
            resp = Response()
            resp.status_code = 404
            req().post.return_value = resp
            req().get.return_value = resp

            with self.assertRaises(RequestException):
                connection.connect()

        self.assertEqual(connection.connected, False)

        # Now disconnect
        with patch('requests.session') as req:
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_post_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.session') as req:
            resp = Response()
            resp.raw = MagicMock()
            resp.status_code = 200
            req().post.return_value = resp
            req().get.return_value = resp
            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            connection.post(mount_point='temp',
                            payload={'payload': 'something'})
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_get_not_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        with self.assertRaises(Exception):
            connection.get(mount_point='temp')

    def test_get_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.session') as req:
            resp = Response()
            resp.raw = MagicMock()
            resp.status_code = 200
            req().post.return_value = resp
            req().get.return_value = resp
            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            connection.get(mount_point='temp')
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_get_connected_change_expected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.session') as req:
            resp = Response()
            resp.raw = MagicMock()
            resp.status_code = 200
            resp2 = Response()
            resp2.raw = MagicMock()
            resp2.status_code = 300
            req().get.side_effect = [resp, resp2]
            req().post.side_effect = [resp, resp, resp2]

            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})

            connection.get(mount_point='temp')
            self.assertEqual(connection.connected, True)
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_delete_not_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        with self.assertRaises(Exception):
            connection.delete(mount_point='temp')

    def test_delete_connected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.session') as req:
            resp = Response()
            resp.raw = MagicMock()
            resp.status_code = 200
            req().post.return_value = resp
            req().get.return_value = resp
            req().delete.return_value = resp
            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            connection.delete(mount_point='temp')
            connection.disconnect()
        self.assertEqual(connection.connected, False)

    def test_delete_connected_change_expected(self):
        connection = Rest(device=self.device, alias='rest', via='rest')
        self.assertEqual(connection.connected, False)

        with patch('requests.session') as req:
            resp = Response()
            resp.raw = MagicMock()
            resp.status_code = 200
            resp2 = Response()
            resp2.raw = MagicMock()
            resp2.status_code = 300
            req().delete.return_value = resp2
            req().post.side_effect = [resp, resp, resp2]
            req().get.return_value = resp
            connection.connect()
            resp.json = MagicMock(return_value={'imdata': []})
            resp2.json = MagicMock(return_value={'imdata': []})
            connection.delete(mount_point='temp')
            self.assertEqual(connection.connected, True)
            connection.disconnect()

        self.assertEqual(connection.connected, False)


if __name__ == '__main__':
    unittest.main()
