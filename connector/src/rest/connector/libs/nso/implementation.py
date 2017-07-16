import re
import json
import logging
import requests
from dicttoxml import dicttoxml
from requests.exceptions import RequestException

from ats.connections import BaseConnection
from rest.connector.implementation import Implementation as RestImplementation

# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(RestImplementation):
    '''Rest Implementation for NSO

    Implementation of Rest connection to Network Service Orchestrator (NSO)

    YAML Example
    ------------

        devices:
            ncs:
                os: nso
                connections:
                    rest:
                        class: rest.connector.Rest
                        ip: 127.0.0.1
                        port: 8080
                        username: admin
                        password: admin
                custom:
                    abstraction:
                        order: [os]

    Code Example
    ------------

        >>> from ats.topology import loader
        >>> testbed = loader.load('ncs.yaml')
        >>> device = testbed.devices['ncs']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected
        True
    '''

    @BaseConnection.locked
    def connect(self, timeout=30, default_content_type='json'):
        '''connect to the device via REST

        Arguments
        ---------

            timeout (int): Timeout value
            default_content_type: Default for content type, json or xml

        Raises
        ------

        Exception
        ---------

            If the connection did not go well

        Note
        ----

        There is no return from this method. If something goes wrong, an
        exception will be raised.

        '''

        if self.connected:
            return

        log.debug("Content type: %s" % default_content_type)
        log.debug("Timeout: %s" % timeout)
        self.content_type = default_content_type

        ip = self.connection_info.ip.exploded
        port = self.connection_info.get('port', '8080')
        self.base_url = 'http://{ip}:{port}'.format(ip=ip, port=port)
        self.login_url = '{f}/api'.format(f=self.base_url)

        log.info("Connecting to '{d}' with alias "
                 "'{a}'".format(d=self.device.name, a=self.alias))

        username = self.connection_info.get('username', 'admin')
        password = self.connection_info.get('password', 'admin')

        self.session = requests.Session()
        self.session.auth = (username, password)

        # Connect to the device via requests
        response = self.session.get(self.login_url, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
            r=response.reason, h=response.headers))
        log.info("Response:\n%s" % output)

        # Make sure it returned requests.codes.ok
        if response.status_code != requests.codes.ok:
            # Something bad happened
            raise RequestException("Connection to '{ip}:{port}' has returned the "
                                   "following code '{c}', instead of the "
                                   "expected status code '{ok}'"\
                                        .format(ip=ip, port=port, c=response.status_code,
                                                ok=requests.codes.ok))
        self._is_connected = True
        log.info("Connected successfully to '{d}'".format(d=self.device.name))

        return output


    @BaseConnection.locked
    def disconnect(self):
        '''disconnect the device for this particular alias'''

        log.info("Disconnecting from '{d}' with "
                 "alias '{a}'".format(d=self.device.name, a=self.alias))
        try:
            self.session.close()
        finally:
            self._is_connected = False
        log.info("Disconnected successfully from "
                 "'{d}'".format(d=self.device.name))


    @BaseConnection.locked
    def get(self, api_url, content_type=None, headers=None,
             expected_status_codes=(
             requests.codes.no_content,
             requests.codes.ok
             ),
            timeout=30):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------
        api_url: API url string
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))
        if content_type is None:
            content_type = self.content_type

        full_url = '{b}{a}'.format(b=self.base_url, a=api_url)

        if content_type.lower() == 'json':
            accept_header = 'application/vnd.yang.data+json' \
             ', application/vnd.yang.collection+json' \
             ', application/vnd.yang.datastore+json'
        elif content_type.lower() == 'xml':
            accept_header = 'application/vnd.yang.data+xml' \
             ', application/vnd.yang.collection+xml' \
             ', application/vnd.yang.datastore+xml'
        else:
            accept_header = content_type

        self.session.headers.update({'Accept': accept_header})
        if headers is not None:
            self.session.headers.update(headers)

        log.info("Sending GET command to '{d}': "\
                 "{u}".format(d=self.device.name, u=full_url))
        log.debug("Headers:{headers}".format(
                    headers= self.session.headers))

        response = self.session.get(full_url, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
            r=response.reason, h=response.headers))
        log.debug("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"\
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_codes,
                                           t=response.text))
        return output


    @BaseConnection.locked
    def post(self, api_url, payload='', content_type=None, headers=None, 
             expected_status_codes=(
             requests.codes.created,
             requests.codes.no_content,
             requests.codes.ok
             ),
             timeout=30):
        '''POST REST Command to configure information from the device

        Arguments
        ---------
        api_url: API url string
        payload: payload to sent, can be string or dict
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        '''

        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        full_url = '{b}{a}'.format(b=self.base_url, a=api_url)

        request_payload = payload
        if isinstance(payload, dict):
            assert content_type != None, 'content_type parameter required when passing dict'
            if content_type == 'json':
                request_payload = json.dumps(payload)
            elif content_type == 'xml':
                request_payload = dicttoxml(payload, attr_type=False)

        if content_type is None:
            if re.match("<", payload.lstrip()) is not None:
                content_type = 'xml'
            else:
                content_type = 'json'

        if content_type.lower() == 'json':
            content_type_header = 'application/vnd.yang.operation+json'
            #content_type_header = 'application/vnd.yang.data+json'
            accept_header = 'application/vnd.yang.data+json' \
             ', application/vnd.yang.collection+json' \
             ', application/vnd.yang.datastore+json'
        elif content_type.lower() == 'xml':
            content_type_header = 'application/vnd.yang.operation+xml'
            #content_type_header = 'application/vnd.yang.data+xml"'
            accept_header = 'application/vnd.yang.data+xml' \
             ', application/vnd.yang.collection+xml' \
             ', application/vnd.yang.datastore+xml'
        else:
            content_type_header = content_type
            accept_header = content_type

        self.session.headers.update({'Content-type': content_type_header})
        self.session.headers.update({'Accept': accept_header})
        if headers is not None:
            self.session.headers.update(headers)

        log.info("Sending POST command to '{d}': {u}"\
            .format(d=self.device.name, u=full_url))
        log.debug("Headers: {h}\nPayload: {p}"\
            .format(h=self.session.headers, p=request_payload))

        # Send to the device
        response = self.session.post(full_url, request_payload, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
            r=response.reason, h=response.headers))
        log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"\
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_codes,
                                           t=response.text))
        return output


    @BaseConnection.locked
    def patch(self, api_url, payload, content_type=None, headers=None, 
             expected_status_codes=(
             requests.codes.created,
             requests.codes.no_content,
             requests.codes.ok
             ),
             timeout=30):
        '''PATCH REST Command to configure information from the device

        Arguments
        ---------
        api_url: API url string
        payload: payload to sent, can be string or dict
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        '''

        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        request_payload = payload
        if isinstance(payload, dict):
            assert content_type != None, 'content_type parameter required when passing dict'
            if content_type == 'json':
                request_payload = json.dumps(payload)
            elif content_type == 'xml':
                request_payload = dicttoxml(payload, attr_type=False)

        full_url = '{b}{a}'.format(b=self.base_url, a=api_url)

        if content_type is None:
            if re.match("<", payload.lstrip()) is not None:
                content_type = 'xml'
            else:
                content_type = 'json'

        if content_type.lower() == 'json':
            content_type_header = 'application/vnd.yang.data+json'
            accept_header = 'application/vnd.yang.data+json' \
             ', application/vnd.yang.collection+json' \
             ', application/vnd.yang.datastore+json'
        elif content_type.lower() == 'xml':
            content_type_header = 'application/vnd.yang.data+xml'
            accept_header = 'application/vnd.yang.data+xml' \
             ', application/vnd.yang.collection+xml' \
             ', application/vnd.yang.datastore+xml'
        else:
            content_type_header = content_type
            accept_header = content_type

        self.session.headers.update({'Content-type': content_type_header})
        self.session.headers.update({'Accept': accept_header})
        if headers is not None:
            self.session.headers.update(headers)

        log.info("Sending PATCH command to '{d}': {u}".format(
                                                    d=self.device.name, u=full_url))
        log.debug("Headers: {h}\nPayload:{p}".format(h=self.session.headers,
                                                    p=request_payload))

        # Send to the device
        response = self.session.patch(full_url, request_payload, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
            r=response.reason, h=response.headers))
        log.debug("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"\
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_codes,
                                           t=response.text))
        return output


    @BaseConnection.locked
    def put(self, api_url, payload, content_type=None, headers=None, 
             expected_status_codes=(
             requests.codes.created,
             requests.codes.no_content,
             requests.codes.ok
             ),
             timeout=30):
        '''PUT REST Command to configure information from the device

        Arguments
        ---------
        api_url: API url string
        payload: payload to sent, can be string or dict
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        '''

        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        full_url = '{b}{a}'.format(b=self.base_url, a=api_url)

        request_payload = payload
        if isinstance(payload, dict):
            assert content_type != None, 'content_type parameter required when passing dict'
            if content_type == 'json':
                request_payload = json.dumps(payload)
            elif content_type == 'xml':
                request_payload = dicttoxml(payload, attr_type=False)

        if content_type is None:
            if re.match("<", payload.lstrip()) is not None:
                content_type = 'xml'
            else:
                content_type = 'json'

        if content_type.lower() == 'json':
            content_type_header = 'application/vnd.yang.data+json'
            accept_header = 'application/vnd.yang.data+json' \
             ', application/vnd.yang.collection+json' \
             ', application/vnd.yang.datastore+json'
        elif content_type.lower() == 'xml':
            content_type_header = 'application/vnd.yang.data+xml'
            accept_header = 'application/vnd.yang.data+xml' \
             ', application/vnd.yang.collection+xml' \
             ', application/vnd.yang.datastore+xml'
        else:
            content_type_header = content_type
            accept_header = content_type

        self.session.headers.update({'Content-type': content_type_header})
        self.session.headers.update({'Accept': accept_header})
        if headers is not None:
            self.session.headers.update(headers)

        log.info("Sending PUT command to '{d}': {u}".format(
                                                    d=self.device.name, u=full_url))
        log.debug("Headers: {h}\nPayload:{p}".format(h=self.session.headers,
                                                    p=request_payload))

        # Send to the device
        response = self.session.put(full_url, request_payload, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
            r=response.reason, h=response.headers))
        log.debug("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"\
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_codes,
                                           t=response.text))
        return output


    @BaseConnection.locked
    def delete(self, api_url, content_type=None, headers=None, 
             expected_status_codes=(
             requests.codes.created,
             requests.codes.no_content,
             requests.codes.ok
             ),
             timeout=30):
        '''DELETE REST Command to configure information from the device

        Arguments
        ---------
        api_url: API url string
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        '''

        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        if content_type is None:
            content_type = self.content_type

        full_url = '{b}{a}'.format(b=self.base_url, a=api_url)

        if content_type.lower() == 'json':
            accept_header = 'application/vnd.yang.data+json'
        elif content_type.lower() == 'xml':
            accept_header = 'application/vnd.yang.data+xml'
        else:
            accept_header = content_type

        self.session.headers.update({'Accept': accept_header})
        if headers is not None:
            self.session.headers.update(headers)

        log.info("Sending DELETE command to '{d}': "\
                 "{u}".format(d=self.device.name, u=full_url))
        log.debug("Headers:{headers}".format(
                    headers= self.session.headers))

        response = self.session.delete(full_url, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
            r=response.reason, h=response.headers))
        log.debug("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"\
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_codes,
                                           t=response.text))
        return output
