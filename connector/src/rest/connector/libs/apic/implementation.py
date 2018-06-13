import json
import logging
import requests
from requests.exceptions import RequestException

from ats.connections import BaseConnection
from rest.connector.implementation import Implementation

# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(Implementation):
    '''Rest Implementation for APIC

    Implementation of Rest connection to devices based on pyATS BaseConnection
    for APIC

    YAML Example
    ------------

        devices:
            apic1:
                connections:
                    rest:
                        class: rest.connector.Rest
                        ip : "2.3.4.5"
                        username: admin
                        password: cisco123

    Code Example
    ------------

        >>> from ats.topology import loader
        >>> testbed = loader.load('/users/xxx/xxx/testbed.yaml')
        >>> device = testbed.devices['apic1']
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
                apic1:
                    connections:
                        rest:
                            class: rest.connector.Rest
                            ip : "2.3.4.5"
                            username: "admin"
                            password: "cisco123"

        Code Example
        ------------

            >>> from ats.topology import loader
            >>> testbed = loader.load('/users/xxx/xxx/testbed.yaml')
            >>> device = testbed.devices['apic1']
            >>> device.connect(alias='rest', via='rest')
        '''

        if self.connected:
            return

        ip = self.connection_info['ip'].exploded
        self.url = 'https://{ip}/'.format(ip=ip)
        login_url = '{f}api/aaaLogin.json'.format(f=self.url)

        payload = {
           "aaaUser": {
              "attributes": {
                 "name": self.device.connections.rest.username,
                 "pwd": self.device.connections.rest.password,
               }
           }
        }

        log.info("Connecting to '{d}' with alias "
                 "'{a}'".format(d=self.device.name, a=self.alias))

        # proxies = {
        #     'http': 'http://proxy.esl.cisco.com:80/',
        #     'https': 'http://proxy.esl.cisco.com:80/',
        # }

        self.session = requests.Session()
        # self.session.proxies = proxies

        _data = json.dumps(payload)

        # Connect to the device via requests
        response = self.session.post(login_url, data=_data, timeout=timeout, \
            verify=False)
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

           There is limitation on the amount of time the session ca be active
           for on the APIC. However, there are no way to verify if
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
    @isconnected
    def get(self, dn, expected_status_code=requests.codes.ok, timeout=30):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            dn (string): Unique distinguished name that describes the object
                         and its place in the tree.
            expected_status_code (int): Expected result
        '''

        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        full_url = "{f}{dn}"\
                          .format(f=self.url,
                                  dn=dn)

        log.info("Sending GET command to '{d}':"\
                 "\nDN: {furl}".format(d=self.device.name, furl=full_url))

        response = self.session.get(full_url, timeout=timeout, verify=False)
        output = response.json()
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
    def post(self, dn, payload, expected_status_code=requests.codes.ok,
             timeout=30):
        '''POST REST Command to configure information from the device

        Arguments
        ---------

            dn (string): Unique distinguished name that describes the object
                         and its place in the tree.
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
        full_url = '{f}{dn}'.format(f=self.url, dn=dn)

        log.info("Sending POST command to '{d}':"\
                 "\nDN: {furl}\nPayload:{p}".format(d=self.device.name,
                                                    furl=full_url,
                                                    p=payload))

        # Send to the device
        response = self.session.post(full_url, payload, timeout=timeout, \
            verify=False)
        output = response.json()
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
    @isconnected
    def delete(self, dn, expected_status_code=requests.codes.ok, timeout=30):
        '''DELETE REST Command to delete information from the device

        Arguments
        ---------

            dn (string): Unique distinguished name that describes the object
                         and its place in the tree.
            expected_status_code (int): Expected result
            timeout (int): Maximum time
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        # Deal with the dn
        full_url = '{f}{dn}'.format(f=self.url, dn=dn)

        log.info("Sending DELETE command to '{d}':"\
                 "\nDN: {furl}".format(d=self.device.name, furl=full_url))

        # Send to the device
        response = self.session.delete(full_url, timeout=timeout, verify=False)
        output = response.json()
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
