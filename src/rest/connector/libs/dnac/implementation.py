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
    '''Rest Implementation for DNAC

    Implementation of Rest connection to devices based on pyATS BaseConnection
    for DNAC

    YAML Example
    ------------

        devices:
            dnac1:
                connections:
                    rest:
                        class: rest.connector.Rest
                        ip : "2.3.4.5"
                        port: 443
                        verify: False
                        credentials:
                            rest:
                                username: admin
                                password: cisco123

    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('/users/xxx/xxx/dna.yaml')
        >>> device = testbed.devices['dnac1']
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
        '''

        if self.connected:
            return

        # Building out Auth request. 
        # prefer host instead of ip address directly
        try:
            host = self.connection_info['host']
        except KeyError:
            host = self.connection_info['ip'].exploded
        
        port = self.connection_info.get('port', 443)
        self.verify = self.connection_info.get('verify', True)

        username, password = get_username_password(self)

        self.base_url = 'https://{host}:{port}'.format(host=host, port=port)

        auth_url  = '{url}/dna/system/api/v1/auth/token'.format(url=self.base_url)
        resp = requests.post(auth_url, headers = STD_HEADER,
                             auth=HTTPBasicAuth(username, password), 
                             verify=self.verify)

        self.token = resp.json()['Token']    # Retrieve the Token from the returned JSONhahhah

        self._is_connected = True
        log.info("Connected successfully to '{d}'".format(d=self.device.name))

    @BaseConnection.locked
    def disconnect(self):
        '''disconnect the device for this particular alias'''

        log.info("Disconnecting from '{d}' with "
                 "alias '{a}'".format(d=self.device.name, a=self.alias))
        self._is_connected = False
        log.info("Disconnected successfully from "
                 "'{d}'".format(d=self.device.name))

    @BaseConnection.locked
    def get(self, api_url, timeout=30, **kwargs):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            api_url (string): API url string
            timeout: timeout in seconds (default: 30)
            **kwargs: keyword arguments supported in requests.get method
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))
        full_url = '{url}{api_url}'.format(url=self.base_url,
                                           api_url=api_url)

        log.debug("Sending GET command to '{d}':"\
                 "\nDN: {furl}".format(d=self.device.name, furl=full_url))

        hdr = {'x-auth-token': self.token, 'content-type' : 'application/json'}
        response = requests.get(full_url, headers=hdr,
                                verify=self.verify, timeout=timeout, **kwargs)
        log.info("Output received:\n{response}".format(response=response))

        return response

    @BaseConnection.locked
    def put(self, api_url, timeout=30, **kwargs):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            api_url (string): API url string
            timeout: timeout in seconds (default: 30)
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))
        full_url = '{url}{api_url}'.format(url=self.base_url,
                                           api_url=api_url)

        log.debug("Sending PUT command to '{d}':"\
                 "\nDN: {furl}".format(d=self.device.name, furl=full_url))

        hdr = {'x-auth-token': self.token, 'content-type' : 'application/json'}
        response = requests.put(full_url, headers=hdr,
                                verify=self.verify, timeout=timeout, **kwargs)
        log.info("Output received:\n{response}".format(response=response.text))

        return response

    @BaseConnection.locked
    def post(self, api_url, timeout=30, **kwargs):
        '''GET REST Command to POST information to the device

        Arguments
        ---------

            api_url (string): API url string
            timeout: timeout in seconds (default: 30)
            **kwargs are the same keyword arguments for the requests lib
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))
        full_url = '{url}{api_url}'.format(url=self.base_url,
                                           api_url=api_url)

        log.info("Sending POST command to '{d}':"\
                 "\nDN: {furl}".format(d=self.device.name, furl=full_url))

        hdr = {'x-auth-token': self.token, 'content-type' : 'application/json'}
        response = requests.post(full_url, headers=hdr,
                                verify=self.verify, timeout=timeout, **kwargs)
        log.info("Output received:\n{response}".format(response=response))

        return response
