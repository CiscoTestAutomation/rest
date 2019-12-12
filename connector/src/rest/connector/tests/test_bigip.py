#!/bin/env python
""" Unit tests for F5 (BigIP) rest.connector """

import os
import unittest
import requests
import requests_mock
from requests.models import Response
from unittest import mock
from unittest.mock import patch, Mock
from requests.exceptions import RequestException

from pyats.topology import loader

from rest.connector import Rest
from icontrol.session import iControlRESTSession

HERE = os.path.dirname(__file__)


class FakeResponse(object):
    status_code = 200

    def json(self):
        return {
            "username": "admin",
            "loginReference": {
                "link": "https://localhost/mgmt/cm/system/authn/providers/tmos/1f44a60e-11a7-3c51-a49f-82983026b41b/login"
            },
            "loginProviderName": "tmos",
            "token": {
                "token": "3UCPWZW66ZHOR6BUMVW56F6Q6K",
                "name": "3UCPWZW66ZHOR6BUMVW56F6Q6K",
                "userName": "admin",
                "authProviderName": "tmos",
                "user": {"link": "https://localhost/mgmt/shared/authz/users/admin"},
                "timeout": 1200,
                "startTime": "2019-12-03T05:25:10.321-0800",
                "address": "1.2.3.4",
                "partition": "[All]",
                "generation": 1,
                "lastUpdateMicros": 1575379510321149,
                "expirationMicros": 1575380710321000,
                "kind": "shared:authz:tokens:authtokenitemstate",
                "selfLink": "https://localhost/mgmt/shared/authz/tokens/3UCPWZW66ZHOR6BUMVW56F6Q6K",
            },
            "generation": 0,
            "lastUpdateMicros": 0,
        }


class FakeResponseTimout(object):
    status_code = 200

    def json(self):
        return {
            "token": {"token": "3UCPWZW66ZHOR6BUMVW56F6Q6K", "timeout": 3600,},
        }


class FakeResponseGet(object):
    status_code = 200

    def json(self):
        return {
            "kind": "tm:ltm:global-settings:global-settingscollectionstate",
            "selfLink": "https://localhost/mgmt/tm/ltm/global-settings?ver=13.0.1",
        }


class FakeResponsePost(object):
    status_code = 200

    def json(self):
        return {
            "kind": "tm:ltm:node:nodestate",
            "name": "wa122",
            "partition": "Common",
            "fullPath": "/Common/wa122",
            "generation": 2139,
            "selfLink": "https://localhost/mgmt/tm/ltm/node/~Common~wa122?ver=13.0.1",
            "address": "119.119.192.194",
            "connectionLimit": 0,
            "dynamicRatio": 1,
            "ephemeral": "false",
            "fqdn": {
                "addressFamily": "ipv4",
                "autopopulate": "disabled",
                "downInterval": 5,
                "interval": "3600",
            },
            "logging": "disabled",
            "monitor": "default",
            "rateLimit": "disabled",
            "ratio": 1,
            "session": "user-enabled",
            "state": "unchecked",
        }


class FakeResponsePatch(object):
    status_code = 200

    def json(self):
        return {
            "kind": "tm:ltm:node:nodestate",
            "name": "wa122",
            "partition": "Common",
            "fullPath": "/Common/wa122",
            "generation": 2140,
            "selfLink": "https://localhost/mgmt/tm/ltm/node/~Common~wa122?ver=13.0.1",
            "address": "119.119.192.194",
            "connectionLimit": 0,
            "dynamicRatio": 1,
            "ephemeral": "false",
            "fqdn": {
                "addressFamily": "ipv4",
                "autopopulate": "disabled",
                "downInterval": 5,
                "interval": "3600",
            },
            "logging": "disabled",
            "monitor": "default",
            "rateLimit": "disabled",
            "ratio": 1,
            "session": "user-disabled",
            "state": "unchecked",
        }


class FakeResponsePut(object):
    status_code = 200

    def json(self):
        return {
            "kind": "tm:ltm:pool:poolstate",
            "name": "wa12",
            "fullPath": "wa12",
            "generation": 2142,
            "selfLink": "https://localhost/mgmt/tm/ltm/pool/wa12?ver=13.0.1",
            "allowNat": "yes",
            "allowSnat": "yes",
            "ignorePersistedWeight": "disabled",
            "ipTosToClient": "pass-through",
            "ipTosToServer": "pass-through",
            "linkQosToClient": "pass-through",
            "linkQosToServer": "pass-through",
            "loadBalancingMode": "round-robin",
            "minActiveMembers": 0,
            "minUpMembers": 0,
            "minUpMembersAction": "failover",
            "minUpMembersChecking": "disabled",
            "queueDepthLimit": 0,
            "queueOnConnectionLimit": "disabled",
            "queueTimeLimit": 0,
            "reselectTries": 0,
            "serviceDownAction": "none",
            "slowRampTime": 10,
            "membersReference": {
                "link": "https://localhost/mgmt/tm/ltm/pool/~Common~wa12/members?ver=13.0.1",
                "isSubcollection": True,
            },
        }


class test_rest_connector(unittest.TestCase):
    def setUp(self):
        self.testbed = loader.load(os.path.join(HERE, "testbed.yaml"))
        self.device = self.testbed.devices["bigip01"]
        self.ip = str(self.device.connections.rest.ip)
        self.username, self.password = "admin", "admin"
        self.url = "https://" + str(self.ip) + "/mgmt/shared/authn/login"
        self.payload = {
            "username": self.username,
            "password": self.password,
            "loginProviderName": "tmos",
        }

    def test_init(self):
        connection = Rest(device=self.device, alias="rest", via="rest")
        self.assertEqual(connection.device, self.device)

        with self.assertRaises(NotImplementedError):
            self.assertRaises(connection.execute())
        with self.assertRaises(NotImplementedError):
            self.assertRaises(connection.configure())

    @patch("icontrol.session.iControlRESTSession.post")
    def test_iCRS(self, mock_connect_post):
        iCRS = iControlRESTSession(self.username, self.password)
        mock_connect_post.return_value.status_code = 200
        mock_connect_post.return_value = FakeResponse()
        response = iCRS.post(self.url, json=self.payload,)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["token"]["token"], "3UCPWZW66ZHOR6BUMVW56F6Q6K"
        )
        self.assertEqual(response.json()["token"]["timeout"], 1200)

    @patch("icontrol.session.iControlRESTSession.patch")
    def test_iCRS_token(self, mock_connect_patch):
        token = FakeResponse().json()["token"]["token"]

        timeout_payload = {"timeout": "3600"}
        timeout_url = "https://" + self.ip + "/mgmt/shared/authz/tokens/token"

        mock_connect_patch.return_value.status_code = 200
        mock_connect_patch.return_value = FakeResponseTimout()

        token_icr_session = iControlRESTSession(
            self.username, self.password, token_to_use=token
        )
        t_timeout = token_icr_session.patch(timeout_url, json=timeout_payload)

        self.assertEqual(
            t_timeout.json()["token"]["token"], "3UCPWZW66ZHOR6BUMVW56F6Q6K"
        )
        self.assertEqual(t_timeout.json()["token"]["timeout"], 3600)

    @patch("icontrol.session.iControlRESTSession.get")
    def test_get(self, mock_connect_get):
        full_url = "https://" + self.ip + "/mgmt/tm/ltm/global-settings"
        token = "3UCPWZW66ZHOR6BUMVW56F6Q6K"

        mock_connect_get.return_value.status_code = 200
        mock_connect_get.return_value = FakeResponseGet()

        icr_session = iControlRESTSession(
            self.username, self.password, token_to_use=token
        )
        get_icr_session = icr_session.get(full_url)

        output = {
            "kind": "tm:ltm:global-settings:global-settingscollectionstate",
            "selfLink": "https://localhost/mgmt/tm/ltm/global-settings?ver=13.0.1",
        }

        self.assertEqual(get_icr_session.json(), output)

    @patch("icontrol.session.iControlRESTSession.post")
    def test_post(self, mock_connect_post):
        full_url = "https://" + self.ip + "/mgmt/tm/ltm/node/"
        token = "3UCPWZW66ZHOR6BUMVW56F6Q6K"

        mock_connect_post.return_value.status_code = 200
        mock_connect_post.return_value = FakeResponsePost()

        icr_session = iControlRESTSession(
            self.username, self.password, token_to_use=token
        )

        data = {"name": "wa122", "partition": "Common", "address": "119.119.192.194"}

        post_icr_session = icr_session.post(full_url, json=data)

        output = {
            "kind": "tm:ltm:node:nodestate",
            "name": "wa122",
            "partition": "Common",
            "fullPath": "/Common/wa122",
            "generation": 2139,
            "selfLink": "https://localhost/mgmt/tm/ltm/node/~Common~wa122?ver=13.0.1",
            "address": "119.119.192.194",
            "connectionLimit": 0,
            "dynamicRatio": 1,
            "ephemeral": "false",
            "fqdn": {
                "addressFamily": "ipv4",
                "autopopulate": "disabled",
                "downInterval": 5,
                "interval": "3600",
            },
            "logging": "disabled",
            "monitor": "default",
            "rateLimit": "disabled",
            "ratio": 1,
            "session": "user-enabled",
            "state": "unchecked",
        }

        self.assertEqual(post_icr_session.json(), output)
        self.assertEqual(post_icr_session.json()["name"], "wa122")
        self.assertEqual(post_icr_session.json()["session"], "user-enabled")

    @patch("icontrol.session.iControlRESTSession.patch")
    def test_patch(self, mock_connect_patch):
        full_url = "https://" + self.ip + "/mgmt/tm/ltm/node/~Common~wa122"
        token = "3UCPWZW66ZHOR6BUMVW56F6Q6K"

        mock_connect_patch.return_value.status_code = 200
        mock_connect_patch.return_value = FakeResponsePatch()

        icr_session = iControlRESTSession(
            self.username, self.password, token_to_use=token
        )

        data = {"session": "user-disabled"}

        patch_icr_session = icr_session.patch(full_url, json=data)

        output = {
            "kind": "tm:ltm:node:nodestate",
            "name": "wa122",
            "partition": "Common",
            "fullPath": "/Common/wa122",
            "generation": 2140,
            "selfLink": "https://localhost/mgmt/tm/ltm/node/~Common~wa122?ver=13.0.1",
            "address": "119.119.192.194",
            "connectionLimit": 0,
            "dynamicRatio": 1,
            "ephemeral": "false",
            "fqdn": {
                "addressFamily": "ipv4",
                "autopopulate": "disabled",
                "downInterval": 5,
                "interval": "3600",
            },
            "logging": "disabled",
            "monitor": "default",
            "rateLimit": "disabled",
            "ratio": 1,
            "session": "user-disabled",
            "state": "unchecked",
        }

        self.assertEqual(patch_icr_session.json(), output)
        self.assertEqual(patch_icr_session.json()["name"], "wa122")
        self.assertEqual(patch_icr_session.json()["session"], "user-disabled")

    @patch("icontrol.session.iControlRESTSession.put")
    def test_put(self, mock_connect_put):
        full_url = "https://" + self.ip + "/mgmt/tm/ltm/pool/wa12"
        token = "3UCPWZW66ZHOR6BUMVW56F6Q6K"

        mock_connect_put.return_value.status_code = 200
        mock_connect_put.return_value = FakeResponsePut()

        icr_session = iControlRESTSession(
            self.username, self.password, token_to_use=token
        )

        data = {"members": "wa122:80"}

        put_icr_session = icr_session.put(full_url, json=data)

        output = {
            "kind": "tm:ltm:pool:poolstate",
            "name": "wa12",
            "fullPath": "wa12",
            "generation": 2142,
            "selfLink": "https://localhost/mgmt/tm/ltm/pool/wa12?ver=13.0.1",
            "allowNat": "yes",
            "allowSnat": "yes",
            "ignorePersistedWeight": "disabled",
            "ipTosToClient": "pass-through",
            "ipTosToServer": "pass-through",
            "linkQosToClient": "pass-through",
            "linkQosToServer": "pass-through",
            "loadBalancingMode": "round-robin",
            "minActiveMembers": 0,
            "minUpMembers": 0,
            "minUpMembersAction": "failover",
            "minUpMembersChecking": "disabled",
            "queueDepthLimit": 0,
            "queueOnConnectionLimit": "disabled",
            "queueTimeLimit": 0,
            "reselectTries": 0,
            "serviceDownAction": "none",
            "slowRampTime": 10,
            "membersReference": {
                "link": "https://localhost/mgmt/tm/ltm/pool/~Common~wa12/members?ver=13.0.1",
                "isSubcollection": True,
            },
        }

        self.assertEqual(put_icr_session.json(), output)

    @patch("icontrol.session.iControlRESTSession.delete")
    def test_delete(self, mock_connect_delete):
        full_url = "https://" + self.ip + "/mgmt/tm/ltm/pool/wa12"
        token = "3UCPWZW66ZHOR6BUMVW56F6Q6K"

        mock_connect_delete.return_value.status_code = 200

        icr_session = iControlRESTSession(
            self.username, self.password, token_to_use=token
        )

        delete_icr_session = icr_session.delete(full_url)

        self.assertEqual(delete_icr_session.status_code, 200)

if __name__ == "__main__":
    unittest.main()
