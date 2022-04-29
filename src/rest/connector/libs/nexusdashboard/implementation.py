__author__ = "Daisy Thangapandi <dthangap@cisco.com>"

import json
import logging
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from pyats.connections import BaseConnection
from rest.connector.implementation import Implementation
from rest.connector.utils import get_username_password

# create a logger for this module
log = logging.getLogger(__name__)
STD_HEADER = {'Content-type': 'application/json'}


class Implementation(Implementation):
    '''Rest Implementation for Nexus Dashboard

    Implementation of Rest connection to devices based on pyATS BaseConnection
    for Nexus Dashboard

    YAML Example
    ------------

        devices:
            nd: 
                os: nexusdashboard
                connections:
                    vty:
                        protocol : ssh
                        ip : "2.3.4.5"
                    rest:
                        class: rest.connector.Rest
                        ip : "2.3.4.5"
                        protocol: https
                        credentials:
                            rest:
                                username: admin
                                password: cisco123

    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('/users/xxx/xxx/ndcisco.yaml')
        >>> device = testbed.devices['nd']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected
        True
    '''

    @BaseConnection.locked
    def connect(self, timeout=10, protocol='https'):
        '''connect to the device via REST

        Arguments
        ---------

            timeout (int): Timeout value
            protocol (str): http or https. Default to https

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
                nd:
                    os: nexusdashboard
                    connections:
                        vty:
                            protocol : ssh
                            ip : "2.3.4.5"
                            protocol: https
                        rest:
                            class: rest.connector.Rest
                            ip : "2.3.4.5"
                            protocol: https
                            credentials:
                                rest:
                                    username: admin
                                    password: cisco123

        Code Example
        ------------

            >>> from pyats.topology import loader
            >>> testbed = loader.load('/users/xxx/xxx/ndcisco.yaml')
            >>> device = testbed.devices['nd']
            >>> device.connect(alias='rest', via='rest')
        '''

        try:
            host = self.connection_info['host']
        except KeyError:
            host = self.connection_info['ip'].exploded

        if 'protocol' in self.connection_info:
            protocol = self.connection_info['protocol']

        self.url = '{protocol}://{host}'.format(protocol=protocol,
                                                          host=host)

        self.verify = self.connection_info.get('verify', True)

        username, password = get_username_password(self)

        _data = json.dumps({'userName': username, 
                            'userPasswd': password, 
                            'domain': "DefaultAuth"})

        login_url = '{url}/login'.format(url=self.url)

        log.info("Connecting to '{d}' with alias "
                 "'{a}'".format(d=self.device.name, a=self.alias))

        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)
        response = self.session.post(login_url, data=_data, headers = STD_HEADER, verify=self.verify)
        log.info(response)

        # Make sure it returned requests.codes.ok
        if response.status_code != requests.codes.ok:
            # Something bad happened
            raise RequestException("Connection to '{ip}' has returned the "
                                   "following code '{c}', instead of the "
                                   "expected status code '{ok}'" \
                                   .format(ip=host, c=response.status_code,
                                           ok=requests.codes.ok))

        self.token = response.json()['jwttoken']  # Retrieve the Token from the returned JSONhahhah

        self._is_connected = True
        log.info("Connected successfully to '{d}'".format(d=self.device.name))
        return self.token


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

           There is limitation on the amount of time the session ca be active
           for on the DCNM devices. However, there are no way to verify if
           session is still active unless sending a command. So, its just
           faster to reconnect every time.
         '''
        def decorated(self, *args, **kwargs):
            # Check if connected
            try:
                log.propagate = False
                self.disconnect()
                self.connect()
                log.propagate = True
                ret = func(self, *args, **kwargs)
            finally:
                log.propagate = True
            return ret
        return decorated

    @BaseConnection.locked
    def _request(self, method, api_url, **kwargs):
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
            raise Exception("'{d}' is not connected for alias '{a}'"
                            .format(d=self.device.name,
                                    a=self.alias))

        # Deal with the dn
        full_url = '{f}{api_url}'.format(f=self.url, api_url=api_url)

        if 'data' in kwargs:
            payload = kwargs['data']
        elif 'json' in kwargs:
            payload = kwargs['json']
        else:
            payload = ''

        log.info("Sending {method} command to '{d}':"
                 "\napi_url: {furl}\nPayload:{payload}"
                 .format(method=method,
                         d=self.device.name,
                         furl=full_url,
                         payload=payload))
        AuthCookie = "AuthCookie={}".format(self.token)
        headers = {
            'Cookie': AuthCookie,
            'Content-type': 'application/json'
        }

        # Send to the device
        response = self.session.request(method=method, url=full_url, headers=headers, **kwargs)


        # Make sure it was successful
        try:
            response.raise_for_status()
        except Exception:
            raise RequestException(
                "'{c}' result code has been returned "
                "for '{d}'.\nResponse from server: "
                "{r}".format(d=self.device.name,
                             c=response.status_code,
                             r=response.text))

        # In case the response cannot be decoded into json
        # warn and return the raw text
        try:
            output = response.json()
            if isinstance(output, list):
                output = {"temproot": output}
        except Exception:
            log.warning('Could not decode json. Returning text!')
            output = response.text

        return output

    @BaseConnection.locked
    @isconnected
    def get(self, api_url, timeout=30):
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
        return self._request('GET', api_url, timeout=timeout)

    @BaseConnection.locked
    @isconnected
    def post(self, api_url, payload, timeout=30):
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
        return self._request('POST', api_url, data=json.dumps(payload), timeout=timeout)

    @BaseConnection.locked
    @isconnected
    def delete(self, api_url, timeout=30):
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
        return self._request('DELETE', api_url, timeout=timeout)

    @BaseConnection.locked
    @isconnected
    def patch(self, api_url, payload, timeout=30):
        """PATCH REST Command to partially update existing information on the device

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
        return self._request('PATCH', api_url, data=json.dumps(payload),
                             timeout=timeout)

    @BaseConnection.locked
    @isconnected
    def put(self, api_url, payload, timeout=30):
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
        return self._request('PUT', api_url, data=json.dumps(payload),
                             timeout=timeout)
