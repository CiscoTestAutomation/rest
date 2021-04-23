import json
import logging
import requests

from requests.exceptions import RequestException

from pyats.connections import BaseConnection
from rest.connector.implementation import Implementation as Imp
from rest.connector.utils import get_token

# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(Imp):
    '''Rest Implementation for Elasticsearch

    Implementation of Rest connection to devices based on pyATS BaseConnection
    for Elasticsearch

    YAML Example
    ------------

        devices:
            elasticsearch:
                os: elasticsearch
                connections:
                    rest:
                        class: rest.connector.Rest
                        ip: "10.1.1.1"
                        port: "9200"
                        protocol: http


    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('testbed.yaml')
        >>> device = testbed.devices['elasticsearch']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected
        True
    '''
    @BaseConnection.locked
    def connect(self, timeout=30, port="9200", protocol='https'):
        '''connect to the device via REST

        Arguments
        ---------

            timeout (int): Timeout value

        Raises
        ------

        Exception
        ---------

            If the connection did not go well

        Note
        ----

        There is no return from this method. If something goes wrong, an
        exception will be raised.


        YAML Example
        ------------

            devices:
                elasticsearch:
                    os: elasticsearch
                    connections:
                        rest:
                            class: rest.connector.Rest
                            ip: "10.1.1.1"
                            port: 9200
                            protocol: http

        Code Example
        ------------

            >>> from pyats.topology import loader
            >>> testbed = loader.load('testbed.yaml')
            >>> device = testbed.devices['elasticsearch']
            >>> device.connect(alias='rest', via='rest')
        '''

        if self.connected:
            return

        if 'host' in self.connection_info:
            ip = self.connection_info['host']
        else:
            ip = self.connection_info['ip'].exploded
        if 'protocol' in self.connection_info:
            protocol = self.connection_info['protocol']
        if 'port' in self.connection_info:
            port = self.connection_info['port']
            self.url = '{protocol}://{ip}:{port}/'.format(protocol=protocol,
                                                          ip=ip,
                                                          port=port)

        self.headers = {
            'Content-Type': 'application/json',
        }

        log.info("Connecting to '{d}' with alias "
                 "'{a}'".format(d=self.device.name, a=self.alias))

        self.session = requests.Session()

        # Connect to the device via requests
        response = self.session.get(self.url, timeout=timeout, \
            headers=self.headers)
        log.info(response)

        # Make sure it returned requests.codes.ok
        if response.status_code != requests.codes.ok:
            # Something bad happened
            raise RequestException("Connection to '{ip}' has returned the "
                                   "following code '{c}', instead of the "
                                   "expected status code '{ok}'"\
                                        .format(ip=ip, c=response.status_code,
                                                ok=requests.codes.ok))
        self._is_connected = True
        log.info("Connected successfully to '{d}'".format(d=self.device.name))

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

    def isconnected(func):
        '''Decorator to make sure session to device is active

           There is limitation on the amount of time the session can be active
           against Elasticsearch. However, there are no way to verify if
           session is still active unless sending a command. So, its just
           faster to reconnect every time.
         '''
        def decorated(self, *args, **kwargs):
            # Check if connected
            try:
                self.disconnect()

                if 'timeout' in kwargs:
                    self.connect(timeout=kwargs['timeout'])
                else:
                    self.connect()
            finally:
                ret = func(self, *args, **kwargs)
            return ret

        return decorated

    @BaseConnection.locked
    def _request(self, method, dn, **kwargs):
        """ Wrapper to send REST command to device

        Args:
            method (str): session request method

            dn (str): rest endpoint

        Returns:
            response.json() or response.text

        Raises:
            RequestException if response is not ok

        """
        if not self.connected:
            raise Exception("'{d}' is not connected for alias '{a}'".format(
                d=self.device.name, a=self.alias))

        # Deal with the dn
        full_url = '{f}{dn}'.format(f=self.url, dn=dn)

        if 'data' in kwargs:
            p = kwargs['data']
        elif 'json' in kwargs:
            p = kwargs['json']
        else:
            p = ''

        expected_return_code = kwargs.pop('expected_return_code', None)

        log.info("Sending {method} command to '{d}':"
                 "\nDN: {furl}\nPayload:{p}".format(method=method,
                                                    d=self.device.name,
                                                    furl=full_url,
                                                    p=p))

        # Send to the device
        response = self.session.request(method=method, url=full_url, **kwargs)

        # An expected return code was provided. Ensure the response has this code.
        if expected_return_code:
            if response.status_code != expected_return_code:
                raise RequestException(
                    "'{c}' result code has been returned for '{d}'.\n"
                    "Expected '{expected_c}' result code.\n"
                    "Response from server: {r}".format(
                        c=response.status_code,
                        d=self.device.name,
                        expected_c=expected_return_code,
                        r=response.text))
        else:
            # No expected return code provided. Make sure it was successful.
            try:
                response.raise_for_status()
            except Exception:
                raise RequestException("'{c}' result code has been returned "
                                       "for '{d}'.\nResponse from server: "
                                       "{r}".format(d=self.device.name,
                                                    c=response.status_code,
                                                    r=response.text))

        log.info("Response from '{dev}':\n"
                 "Result Code: {c}\n"
                 "Response: {r}".format(dev=self.device.name,
                                        c=response.status_code,
                                        r=response.text))

        # In case the response cannot be decoded into json
        # warn and return the raw text
        if response.text:
            try:
                output = response.json()
            except Exception:
                log.warning('Could not decode json. Returning text!')
                output = response.text
        else:
            output = response.text

        return output

    @BaseConnection.locked
    @isconnected
    def get(self, dn, headers=None, timeout=30, **kwargs):
        """ GET REST Command to retrieve information from the device

        Args:
            dn (str): Unique distinguished name that describes the object
                      and its place in the tree.

            headers (dict): Headers to send with the rest call

            timeout (int): Maximum time to allow rest call to return

        Returns:
            response.json() or response.text

        Raises:
            RequestException if response is not ok
        """
        if not headers:
            headers = self.headers

        return self._request('GET',
                             dn,
                             headers=headers,
                             timeout=timeout,
                             **kwargs)

    @BaseConnection.locked
    @isconnected
    def post(self, dn, payload, headers=None, timeout=30, **kwargs):
        """POST REST Command to configure new information on the device

        Args:
            dn (string): Unique distinguished name that describes the object
                         and its place in the tree.

            payload (dict): Dictionary containing the information to send via
                            the post

            headers (dict): Headers to send with the rest call

            timeout (int): Maximum time

        Returns:
            response.json() or response.text

        Raises:
            RequestException if response is not ok
        """
        if not headers:
            headers = self.headers

        if not isinstance(payload, str):
            payload = json.dumps(payload)

        return self._request('POST',
                             dn,
                             data=payload,
                             headers=headers,
                             timeout=timeout,
                             **kwargs)

    @BaseConnection.locked
    @isconnected
    def delete(self, dn, headers=None, timeout=30, **kwargs):
        """DELETE REST Command to delete information from the device

        Args
            dn (string): Unique distinguished name that describes the object
                         and its place in the tree.

            headers (dict): Headers to send with the rest call

            timeout (int): Maximum time

        Returns:
            response.json() or response.text

        Raises:
            RequestException if response is not ok
        """
        if not headers:
            headers = self.headers

        return self._request('DELETE',
                             dn,
                             headers=headers,
                             timeout=timeout,
                             **kwargs)

    @BaseConnection.locked
    @isconnected
    def put(self, dn, payload, headers=None, timeout=30, **kwargs):
        """PUT REST Command to update existing information on the device

        Args
            dn (string): Unique distinguished name that describes the object
                         and its place in the tree.

            payload (dict): Dictionary containing the information to send via
                            the post

            headers (dict): Headers to send with the rest call

            timeout (int): Maximum time

        Returns:
            response.json() or response.text

        Raises:
            RequestException if response is not ok
        """
        if not headers:
            headers = self.headers

        if type(payload) == str:
            payload = json.loads(payload)

        return self._request('PUT',
                             dn,
                             data=payload,
                             headers=headers,
                             timeout=timeout,
                             **kwargs)
