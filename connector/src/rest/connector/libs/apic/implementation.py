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
                        credentials:
                            rest:
                                username: admin
                                password: cisco123

    Code Example
    ------------

        >>> from pyats.topology import loader
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
                            credentials:
                                rest:
                                    username: admin
                                    password: cisco123

        Code Example
        ------------

            >>> from pyats.topology import loader
            >>> testbed = loader.load('/users/xxx/xxx/testbed.yaml')
            >>> device = testbed.devices['apic1']
            >>> device.connect(alias='rest', via='rest')
        '''

        if self.connected:
            return

        ip = self.connection_info['ip'].exploded
        self.url = 'https://{ip}/'.format(ip=ip)
        login_url = '{f}api/aaaLogin.json'.format(f=self.url)

        username, password = get_username_password(self)

        payload = {
           "aaaUser": {
              "attributes": {
                 "name": username,
                 "pwd": password,
               }
           }
        }

        log.info("Connecting to '{d}' with alias "
                 "'{a}'".format(d=self.device.name, a=self.alias))

        self.session = requests.Session()

        # Connect to the device via requests
        response = self.session.post(login_url, json=payload, timeout=timeout, \
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

           There is limitation on the amount of time the session cab be active
           on the APIC. However, there are no way to verify if
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
    def get(self, dn, query_target='self', rsp_subtree='no', \
            query_target_filter='', rsp_prop_include='all', \
            rsp_subtree_include='', rsp_subtree_class='',\
            expected_status_code=requests.codes.ok, timeout=30):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            dn (string): Unique distinguished name that describes the object
                         and its place in the tree.
            query_target {self|children|subtree}: 
                                'self': (default) MO itself
                                'children': just the MO's child objects
                                'subtree': MO and its child objects
            rsp_subtree {no|children|full}: Specifies child object level 
                                            included in the response
                                            'no': (default) the response
                                                   does not include any children
                                            'children': return only the child 
                                                        objects
                                            'full': includes the full tree 
                                                    structure
            rsp_prop_include {all|naming-only|config-only}:
                                'all': all properties of the objects
                                'naming-only': only the naming properties
                                'config-only': only configurable properties
            rsp_subtree_include (string): specify additional contained objects 
                                          or options to be included
            rsp_subtree_class (string) : specify classes
            query_target_filter (string): filter expression
            expected_status_code (int): Expected result
        '''

        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        full_url = "{f}{dn}?query-target={qt}&rsp-subtree={rs}"\
                        "&rsp-prop-include={rpi}"\
                          .format(f=self.url,
                                  dn=dn,
                                  qt=query_target,
                                  rs=rsp_subtree,
                                  rpi=rsp_prop_include)
        if query_target_filter:
            full_url += "&query-target-filter={qtf}"\
                .format(qtf=query_target_filter)

        if rsp_subtree_include:
            full_url += "&rsp-subtree-include={rsi}"\
                .format(rsi=rsp_subtree_include)

        if rsp_subtree_class:
            full_url += "&rsp-subtree-class={rsc}"\
                .format(rsc=rsp_subtree_class)

        log.info("Sending GET command to '{d}':"\
                 "\nDN: {furl}".format(d=self.device.name, furl=full_url))

        response = self.session.get(full_url, timeout=timeout, verify=False)
        
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
                                   "'{e}' for '{d}', got:\n {msg}"\
                                   .format(d=self.device.name,
                                           c=response.status_code,
                                           e=expected_status_code,
                                           msg=response.text))
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
