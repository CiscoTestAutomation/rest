import json
import logging
import requests
import os
from requests.exceptions import RequestException
from pyats.connections import BaseConnection
from rest.connector.implementation import Implementation as RestImplementation
from rest.connector.utils import get_token

# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(RestImplementation):
    '''Rest Implementation for xpresso

    Implementation of Rest connection to devices based on pyATS BaseConnection
    for xpresso

    YAML Example
    ------------

        devices:
            xpresso:
                os: xpresso
                connections:
                    rest:
                        class: rest.connector.Rest
                        host : "xpresso.cisco.com"
                        credentials:
                            rest:
                                token: <xpressoaccesstoken>

    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('testbed.yaml')
        >>> device = testbed.devices['xpresso']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected
        True
    '''
    @BaseConnection.locked
    def connect(self, timeout=30):
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
            xpresso:
                os: xpresso
                connections:
                    rest:
                        class: rest.connector.Rest
                        host : "xpresso.cisco.com"
                        protocol: http
                        credentials:
                            rest:
                                token: <xpressoaccesstoken>

        Code Example
        ------------

            >>> from pyats.topology import loader
            >>> testbed = loader.load('testbed.yaml')
            >>> device = testbed.devices['xpresso']
            >>> device.connect(alias='rest', via='rest')
        '''

        if self.connected:
            return True

        host = self.connection_info.get('host')
        if not host:
            raise Exception("must include a host name")

        protocol = self.connection_info.get('protocol', 'https')
         
        if 'port' in self.connection_info:
            port = self.connection_info['port']
            self.url = f'{protocol}://{host}:{port}/'
        else:
            self.url = f'{protocol}://{host}/'

        # get authentication data
        token = get_token(self)
        if token is None:
            raise Exception("must include an access token for rest")

        # start sesssion
        log.info(f"Connecting to {self.device.name} with alias {self.alias}")
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers.update({"Authorization": token})

        # attempt to get <host>
        try:
            resp = self.session.get(self.url)
        except Exception as e:
            raise Exception(
                f"could not connect to provided host. Verify host, port and protocol: {e}"
            )

        if resp.status_code != requests.codes.ok:
            raise RequestException(
                f"Connection to {self.url} returned {resp.status_code}"
                f" instead of 200, verify the host, port and protocol")
        
        self._is_connected = True
        log.info(f"Connected successfully to {self.device.name}")

    @BaseConnection.locked
    def disconnect(self):
        '''disconnect the device for this particular alias'''
        log.info(f"Disconnecting from {self.device.name} with alias {self.alias}")
        try:
            self.session.close()
        finally:
            self._is_connected = False
            log.info(f"Disconnected successfully from {self.device.name}")

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
            raise Exception(f"{self.device.name} is not connected for alias {self.alias}")

        # format url, payload, headers
        full_url = f"{self.url}{dn}"
        headers = kwargs.get('headers')
        payload = kwargs.get('json')
        if type(payload) == str:
            payload = json.loads(payload)

        log.info(f"Sending {method} to {self.device.name}\n"
                 f"DN: {full_url}\n"
                 f"Header: {headers}\n"
                 f"Payload: {payload}")

        # Send to the device
        response = self.session.request(method=method, 
                                        url=full_url, 
                                        json=payload,
                                        headers=headers)

        # An expected return code was provided. Ensure the response has this code.
        expected_return_code = kwargs.pop('expected_return_code', None)
        if expected_return_code:
            if response.status_code != expected_return_code:
                raise RequestException(
                    f"Returned status code: {response.status_code}\n"
                    f"Expected: {expected_return_code}\n"
                    f"Response: {response.text}"
                )
        else:
            # No expected return code provided. Make sure it was successful.
            try:
                response.raise_for_status()
            except Exception:
                raise RequestException(
                    f"Returned status code: {response.status_code}\n"
                    f"Response: {response.text}"
                )
        
        # print returned data from server
        log.info(f"Response from {self.device.name}\n"
                 f"Result code: {response.status_code}\n"
                 f"Response: {response.text}")

        # In case the response cannot be decoded into json
        # warn and return the raw text
        try:
            output = response.json()
        except Exception:
            log.warning('Could not decode json. Returning text!')
            output = response.text
        return output

    @BaseConnection.locked
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
        return self._request('GET',
                             dn,
                             headers=headers,
                             timeout=timeout,
                             **kwargs)

    @BaseConnection.locked
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
        return self._request('POST',
                             dn,
                             json=payload,
                             headers=headers,
                             timeout=timeout,
                             **kwargs)

    @BaseConnection.locked
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
        return self._request('DELETE',
                             dn,
                             headers=headers,
                             timeout=timeout,
                             **kwargs)

    @BaseConnection.locked
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
        return self._request('PUT',
                             dn,
                             json=payload,
                             headers=headers,
                             timeout=timeout,
                             **kwargs)
