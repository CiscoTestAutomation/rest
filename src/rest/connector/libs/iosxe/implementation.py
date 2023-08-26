import json
import logging
import re
import urllib.request
import requests
from dict2xml import dict2xml
from requests.exceptions import RequestException

from pyats.connections import BaseConnection
from rest.connector.implementation import Implementation as RestImplementation
from rest.connector.utils import get_username_password

# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(RestImplementation):
    '''Rest Implementation for IOS-XE

    Implementation of Rest connection to IOS-XE devices supporting RESTCONF

    YAML Example
    ------------

        devices:
            eWLC:
                os: iosxe
                connections:
                    rest:
                        class: rest.connector.Rest
                        ip: 127.0.0.1
                        port: "443"
                        protocol: https
                        credentials:
                            rest:
                                username: admin
                                password: admin
                custom:
                    abstraction:
                        order: [os]

    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('topology.yaml')
        >>> device = testbed.devices['eWLC']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected
        True
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'proxies' not in kwargs:
            self.proxies = urllib.request.getproxies()

    @BaseConnection.locked
    def connect(self,
                timeout=30,
                default_content_type='json',
                verbose=False,
                port="443",
                protocol='https'):
        '''connect to the device via REST

        Arguments
        ---------

            timeout (int): Timeout value
            default_content_type: Default for content type, json or xml
            proxies: Specify the proxy to use for connection as seen below.
                    {'http': 'http://proxy.esl.cisco.com:80/',
                    'ftp': 'http://proxy.esl.cisco.com:80/',
                    'https': 'http://proxy.esl.cisco.com:80/',
                    'no': '.cisco.com'}

        Raises
        ------

        Exception
        ---------

            If the connection did not go well

        Note
        ----

        Connecting via RESTCONF does not require contacting the device.
        This does nothing

        '''
        if self.connected:
            return

        log.debug("Content type: %s" % default_content_type)
        log.debug("Timeout: %s" % timeout)
        self.content_type = default_content_type

        # support sshtunnel
        if 'sshtunnel' in self.connection_info:
            try:
                from unicon.sshutils import sshtunnel
            except ImportError:
                raise ImportError(
                    '`unicon` is not installed for `sshtunnel`. Please install by `pip install unicon`.'
                )
            try:
                tunnel_port = sshtunnel.auto_tunnel_add(self.device, self.via)
                if tunnel_port:
                    ip = self.device.connections[self.via].sshtunnel.tunnel_ip
                    port = tunnel_port
            except AttributeError as e:
                raise AttributeError(
                    "Cannot add ssh tunnel. Connection %s may not have ip/host or port.\n%s"
                    % (self.via, e))
        else:
            ip = self.connection_info.ip.exploded
            port = self.connection_info.get('port', port)

        if 'protocol' in self.connection_info:
            protocol = self.connection_info['protocol']

        self.base_url = '{protocol}://{ip}:{port}'.format(protocol=protocol,
                                                          ip=ip,
                                                          port=port)

        # ---------------------------------------------------------------------
        # Connect to "well-known" RESTCONF resource to "test", the
        # RESTCONF connection on 'connect'. Comparable to CLI (SSH) connection,
        # which triggers a "show version" on connect
        # ---------------------------------------------------------------------
        log.info("Connecting to '{d}' with alias "
                 "'{a}'".format(d=self.device.name, a=self.alias))
        login_url = '{f}/restconf/data/Cisco-IOS-XE-native:native/version'.format(f=self.base_url)
        username, password = get_username_password(self)

        self.session = requests.Session()
        self.session.auth = (username, password)

        header = 'application/yang-data+{fmt}'

        if default_content_type.lower() == 'json':
            accept_header = header.format(fmt='json')
        elif default_content_type.lower() == 'xml':
            accept_header = header.format(fmt='xml')
        else:
            accept_header = default_content_type
        
        self.session.headers.update({'Accept': accept_header})

        # Connect to the device via requests
        response = self.session.get(
            login_url, proxies=self.proxies, timeout=timeout, verify=False)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}, payload {p}".format(
            c=response.status_code,
            r=response.reason,
            h=response.headers,
            p=response.text))
        if verbose:
            log.info("Response text:\n%s" % output)

        # Make sure it returned requests.codes.ok
        if response.status_code != requests.codes.ok:
            # Something bad happened
            raise RequestException("Connection to '{ip}:{port}' has returned the "
                                   "following code '{c}', instead of the "
                                   "expected status code '{ok}'"
                                   .format(ip=ip, port=port, c=response.status_code,
                                           ok=requests.codes.ok))
        self._is_connected = True
        log.info("Connected successfully to '{d}'".format(d=self.device.name))

        return response

    @BaseConnection.locked
    def disconnect(self):
        """
            Does not make sense to disconnect from a device.
        """
        self._is_connected = False
        return

    @BaseConnection.locked
    def get(self, api_url, content_type=None, headers=None,
            expected_status_codes=(
                requests.codes.no_content,
                requests.codes.ok
            ),
            timeout=30,
            verbose=False):
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

        header = 'application/yang-data+{fmt}'

        if content_type.lower() == 'json':
            accept_header = header.format(fmt='json')
        elif content_type.lower() == 'xml':
            accept_header = header.format(fmt='xml')
        else:
            accept_header = content_type

        self.session.headers.update({'Accept': accept_header})
        if headers is not None:
            self.session.headers.update(headers)

        log.debug("Sending GET command to '{d}': "
                 "{u}".format(d=self.device.name, u=full_url))
        log.debug("Request headers:{headers}".format(
            headers=self.session.headers))

        response = self.session.get(full_url, proxies=self.proxies, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
                                                           r=response.reason, h=response.headers))
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_codes,
                                           t=response.text))
        return response

    @BaseConnection.locked
    def post(self, api_url, payload='', content_type=None, headers=None,
             expected_status_codes=(
                 requests.codes.created,
                 requests.codes.no_content,
                 requests.codes.ok
             ),
             timeout=30,
             verbose=False):
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
            assert content_type is not None, 'content_type parameter required when passing dict'
            if content_type == 'json':
                request_payload = json.dumps(payload)
            elif content_type == 'xml':
                request_payload = dict2xml(payload)

        if content_type is None:
            if re.match("<", payload.lstrip()) is not None:
                content_type = 'xml'
            else:
                content_type = 'json'

        content_type_header = 'application/yang-data+{fmt}'
        accept_header = 'application/yang-data+{fmt}'

        if content_type.lower() == 'json':
            content_type_header = content_type_header.format(fmt='json')
            accept_header = accept_header.format(fmt='json')
        elif content_type.lower() == 'xml':
            content_type_header = content_type_header.format(fmt='xml')
            accept_header = accept_header.format(fmt='xml')
        else:
            content_type_header = content_type
            accept_header = content_type

        self.session.headers.update({'Content-type': content_type_header})
        self.session.headers.update({'Accept': accept_header})
        if headers is not None:
            self.session.headers.update(headers)

        log.debug("Sending POST command to '{d}': {u}"
                 .format(d=self.device.name, u=full_url))
        log.debug("Request headers: {h}\nPayload: {p}"
                  .format(h=self.session.headers, p=request_payload))
        if verbose:
            log.info('Request payload:\n{payload}'.format(
                payload=request_payload))

        # Send to the device
        response = self.session.post(
            full_url, request_payload, proxies=self.proxies, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
                                                           r=response.reason, h=response.headers))
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_codes,
                                           t=response.text))
        return response

    @BaseConnection.locked
    def patch(self, api_url, payload, content_type=None, headers=None,
              expected_status_codes=(
                  requests.codes.created,
                  requests.codes.no_content,
                  requests.codes.ok
              ),
              timeout=30,
              verbose=False):
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
            assert content_type is not None, 'content_type parameter required when passing dict'
            if content_type == 'json':
                request_payload = json.dumps(payload)
            elif content_type == 'xml':
                request_payload = dict2xml(payload)

        full_url = '{b}{a}'.format(b=self.base_url, a=api_url)

        if content_type is None:
            if re.match("<", payload.lstrip()) is not None:
                content_type = 'xml'
            else:
                content_type = 'json'

        content_type_header = 'application/yang-data+{fmt}'
        accept_header = 'application/yang-data+{fmt}'

        if content_type.lower() == 'json':
            content_type_header = content_type_header.format(fmt='json')
            accept_header = accept_header.format(fmt='json')
        elif content_type.lower() == 'xml':
            content_type_header = content_type_header.format(fmt='xml')
            accept_header = accept_header.format(fmt='xml')
        else:
            content_type_header = content_type
            accept_header = content_type

        self.session.headers.update({'Content-type': content_type_header})
        self.session.headers.update({'Accept': accept_header})
        if headers is not None:
            self.session.headers.update(headers)

        log.debug("Sending PATCH command to '{d}': {u}".format(
            d=self.device.name, u=full_url))
        log.debug("Request headers: {h}\nPayload:{p}".format(h=self.session.headers,
                                                             p=request_payload))
        if verbose:
            log.info('Request payload:\n{payload}'.format(
                payload=request_payload))

        # Send to the device
        response = self.session.patch(
            full_url, request_payload, proxies=self.proxies, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
                                                           r=response.reason, h=response.headers))
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_codes,
                                           t=response.text))
        return response

    @BaseConnection.locked
    def put(self, api_url, payload, content_type=None, headers=None,
            expected_status_codes=(
                requests.codes.created,
                requests.codes.no_content,
                requests.codes.ok
            ),
            timeout=30,
            verbose=False):
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
                request_payload = dict2xml(payload)

        if content_type is None:
            if re.match("<", payload.lstrip()) is not None:
                content_type = 'xml'
            else:
                content_type = 'json'

        content_type_header = 'application/yang-data+{fmt}'
        accept_header = 'application/yang-data+{fmt}'

        if content_type.lower() == 'json':
            content_type_header = content_type_header.format(fmt='json')
            accept_header = accept_header.format(fmt='json')
        elif content_type.lower() == 'xml':
            content_type_header = content_type_header.format(fmt='xml')
            accept_header = accept_header.format(fmt='xml')
        else:
            content_type_header = content_type
            accept_header = content_type

        self.session.headers.update({'Content-type': content_type_header})
        self.session.headers.update({'Accept': accept_header})
        if headers is not None:
            self.session.headers.update(headers)

        log.debug("Sending PUT command to '{d}': {u}".format(
            d=self.device.name, u=full_url))
        log.debug("Request headers: {h}\nPayload:{p}".format(h=self.session.headers,
                                                             p=request_payload))
        if verbose:
            log.info('Request payload:\n{payload}'.format(
                payload=request_payload))

        # Send to the device
        response = self.session.put(full_url, request_payload, proxies=self.proxies, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
                                                           r=response.reason, h=response.headers))
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_codes,
                                           t=response.text))
        return response

    @BaseConnection.locked
    def delete(self, api_url, content_type=None, headers=None,
               expected_status_codes=(
                   requests.codes.created,
                   requests.codes.no_content,
                   requests.codes.ok
               ),
               timeout=30,
               verbose=False):
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
            accept_header = 'application/yang-data+json'
        elif content_type.lower() == 'xml':
            accept_header = 'application/yang-data+xml'
        else:
            accept_header = content_type

        self.session.headers.update({'Accept': accept_header})
        if headers is not None:
            self.session.headers.update(headers)

        log.debug("Sending DELETE command to '{d}': "
                 "{u}".format(d=self.device.name, u=full_url))
        log.debug("Request headers:{headers}".format(
            headers=self.session.headers))

        response = self.session.delete(full_url, proxies=self.proxies, timeout=timeout)
        output = response.text
        log.debug("Response: {c} {r}, headers: {h}".format(c=response.status_code,
                                                           r=response.reason, h=response.headers))
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_codes,
                                           t=response.text))
        return response