import json
import logging
import requests

from requests.exceptions import RequestException


from pyats.connections import BaseConnection
from rest.connector.implementation import Implementation
from rest.connector.utils import get_username_password

# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(Implementation):
    '''Rest Implementation for VIRL

    Implementation of Rest connection to devices based on pyATS BaseConnection
    for VIRL

    YAML Example
    ------------

        devices:
            virl:
                connections:
                    rest:
                        class: rest.connector.Rest
                        ip : "192.168.1.1"
                        credentials:
                            default:
                                username: admin
                                password: cisco123

    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('/users/xxx/xxx/testbed.yaml')
        >>> device = testbed.devices['virl']
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
                virl:
                    connections:
                        rest:
                            class: rest.connector.Rest
                            ip : "192.168.1.1"
                            credentials:
                                default:
                                    username: admin
                                    password: cisco123

        Code Example
        ------------

            >>> from pyats.topology import loader
            >>> testbed = loader.load('/users/xxx/xxx/testbed.yaml')
            >>> device = testbed.devices['virl']
            >>> device.connect(alias='rest', via='rest')
        '''

        if self.connected:
            return

        ip = self.connection_info['ip'].exploded
        port = self.connection_info.get('port', 19399)
        self.url = 'http://{ip}:{port}'.format(ip=ip, port=port)

        self.username, self.password = get_username_password(self)
        self.headers = {"Content-Type": "text/xml;charset=UTF-8"}

        log.info("Connecting to '{d}' with alias "
                 "'{a}'".format(d=self.device.name, a=self.alias))

        self.session = requests.Session()

        # Connect to the device via requests
        response = self.session.get(self.url+'/roster/rest/test',
                                    auth=(self.username, self.password),
                                    timeout=timeout,
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

           There is limitation on the amount of time the session cab be active
           on the VIRL. However, there are no way to verify if
           session is still active unless sending a command. So, its just
           faster to reconnect every time.
         '''
        def decorated(self, *args, **kwargs):
            # Check if connected
            try:
                self.disconnect()
                self.connect()
            finally:
                ret = func(self, *args, **kwargs)
            return ret
        return decorated

    @BaseConnection.locked
    @isconnected
    def get(self, url, \
            expected_status_code=requests.codes.ok, timeout=30, **kwargs):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            url (string): REST API url
            expected_status_code (int): Expected result
        '''

        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        full_url = "{f}{url}"\
            .format(f=self.url, url=url)

        log.debug("Sending GET command to '{d}':"\
                 "\nurl: {url}".format(d=self.device.name, url=full_url))

        response = self.session.get(full_url,
                                    auth=(self.username, self.password),
                                    timeout=timeout,
                                    headers=self.headers,
                                    **kwargs)

        try:
            output = response.json()
        except Exception:
            output = response.text

        log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException("Sending '{furl} to '{d} has returned the "
                                   "following code '{c}', instead of the "
                                   "expected status code '{e}'"
                                   "'{e}'".format(furl=full_url,
                                                  d=self.device.name,
                                                  c=response.status_code,
                                                  e=expected_status_code))
        return output

    @BaseConnection.locked
    @isconnected
    def post(self, url, payload, expected_status_code=requests.codes.ok,
             timeout=30, **kwargs):
        '''POST REST Command to configure information from the device

        Arguments
        ---------

            url (string): API url
            payload (dict): Dictionary containing the information to send via
                            the post
            expected_status_code (int): Expected result
            timeout (int): Maximum time
        '''

        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))
        # Deal with the dn
        full_url = '{f}{url}'.format(f=self.url, url=url)

        log.debug("Sending POST command to '{d}':"\
                 "\nDN: {furl}\nPayload:{p}".format(d=self.device.name,
                                                    furl=full_url,
                                                    p=payload))

        # Send to the device
        response = self.session.post(full_url,
                                     payload,
                                     auth=(self.username, self.password),
                                     timeout=timeout,
                                     headers=self.headers,
                                     **kwargs)
        try:
            output = response.json()
        except Exception:
            output = response.text

        log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code "
                                   "'{e}' for '{d}', got:\n {msg}"\
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_code,
                                           msg=response.text))
        return output

    @BaseConnection.locked
    @isconnected
    def delete(self, url, expected_status_code=requests.codes.ok, timeout=30, **kwargs):
        '''DELETE REST Command to delete information from the device

        Arguments
        ---------

            url (string): API url
            expected_status_code (int): Expected result
            timeout (int): Maximum time
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        full_url = '{f}{url}'.format(f=self.url, url=url)

        log.debug("Sending DELETE command to '{d}':"\
                 "\nurl: {url}".format(d=self.device.name, url=full_url))

        # Send to the device
        response = self.session.delete(full_url,
                                       auth=(self.username, self.password),
                                       headers=self.headers,
                                       timeout=timeout,
                                       **kwargs)

        try:
            output = response.json()
        except Exception:
            output = response.text

        log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code "
                                   "'{e}' for '{d}'"\
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_code))
        return output

    @BaseConnection.locked
    def put(self, url, timeout=30, **kwargs):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            url (string): API url
            timeout: timeout in seconds (default: 30)
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        full_url = '{f}{url}'.format(f=self.url,
                                           url=url)

        log.debug("Sending PUT command to '{d}':"\
                 "\nurl: {url}".format(d=self.device.name, url=full_url))

        response = requests.put(full_url, auth=(self.username, self.password),
                                headers=self.headers, timeout=timeout, **kwargs)

        try:
            output = response.json()
        except Exception:
            output = response.text

        log.info("Output received:\n{output}".format(output=output))

        return output
