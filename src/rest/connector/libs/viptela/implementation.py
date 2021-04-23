import json
import logging
import requests

from pyats.connections import BaseConnection
from rest.connector.implementation import Implementation
from rest.connector.utils import get_username_password

from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(Implementation):
    '''Rest Implementation for viptela/vManage

    Implementation of Rest connection to devices based on pyATS BaseConnection
    for vManage

    YAML Example
    ------------

        devices:
            vmanage:
                os: viptela
                type: vmanage
                custom:
                    abstraction:
                        order: [os]
                connections:
                    rest:
                        class: rest.connector.Rest
                        ip : "2.3.4.5"
                        port: "8443"
                        verify: False
                        protocol: https
                        credentials:
                            rest:
                                username: admin
                                password: cisco123

    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('/users/xxx/xxx/sdwan.yaml')
        >>> device = testbed.devices['vmanage']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected
        True
    '''

    @BaseConnection.locked
    def connect(self, timeout=30, port="8443", protocol='https'):
        '''connect to the device via REST

        Arguments
        ---------

            timeout (int): Timeout value
            port (str): Port number. Default to 8443
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
        '''

        if self.connected:
            return

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
            ip = self.connection_info['ip'].exploded
            port = self.connection_info.get('port', port)

        if 'protocol' in self.connection_info:
            protocol = self.connection_info['protocol']

        self.base_url = '{protocol}://{ip}:{port}'.format(protocol=protocol,
                                                          ip=ip,
                                                          port=port)

        self.verify = self.connection_info.get('verify', False)

        username, password = get_username_password(self)


        login_action = '/j_security_check'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # Format data for loginForm
        login_data = {'j_username': username, 'j_password': password}

        # Url for posting login data
        login_url = self.base_url + login_action

        token_url = '{url}/dataservice/client/token'.format(url=self.base_url)

        self.session = requests.session()
        resp = self.session.post(login_url,
                                 data=login_data,
                                 headers=headers,
                                 verify=self.verify,
                                 timeout=timeout)

        if resp.status_code == 200:
            # html login page gets returned if credentials are invalid
            if resp.content and b'Invalid User or Password' in resp.content:
                raise RequestException(
                    "Failed to login '{d}'".format(d=self.device.name))

            log.info("Login successfully to '{d}'".format(d=self.device.name))
        else:
            raise RequestException(
                "Failed to login '{d}'".format(d=self.device.name))

        login_token = self.session.get(url=token_url,
                                       verify=self.verify,
                                       timeout=timeout)

        if login_token.status_code == 200:
            self.token = login_token.content
        else:
            raise RequestException(
                "Failed to get token for '{d}'".format(d=self.device.name))

        self._is_connected = True
        log.info("Connected successfully to '{d}'".format(d=self.device.name))
        self.default_headers = {'X-XSRF-TOKEN': self.token,
                                'Content-Type': 'application/json'}

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
    def get(self,
            mount_point,
            headers=None,
            timeout=30):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            mount_point (string): API url string
            headers (dict): Additional headers dictionary
            timeout: timeout in seconds (default: 30)
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        data_url = self.base_url
        full_url = '{url}/{mount_point}'.format(
            url=data_url,
            mount_point=mount_point)

        log.info("Sending GET command to '{d}':"
                 "\nDN: {furl}".format(d=self.device.name, furl=full_url))

        hdr = self.default_headers

        if headers is not None:
            hdr.update(headers)

        response = self.session.get(full_url, headers=hdr,
                                    verify=self.verify, timeout=timeout)
        log.info("Output received:\n{response}".format(response=response))

        return response

    @BaseConnection.locked
    def post(self,
             mount_point,
             payload,
             headers=None,
             timeout=30):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            mount_point (string): API url string
            payload (dict): payload dictionary
            headers (dict): Additional headers dictionary
            timeout: timeout in seconds (default: 30)
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        data_url = self.base_url
        full_url = '{url}/{mount_point}'.format(
            url=data_url,
            mount_point=mount_point)

        log.info("Sending POST command to '{d}':"
                 "\nDN: {furl}".format(d=self.device.name, furl=full_url))

        if isinstance(payload, dict):
            payload = json.dumps(payload)

        hdr = self.default_headers

        if headers is not None:
            hdr.update(headers)

        response = self.session.post(full_url, data=payload, headers=hdr,
                                     verify=self.verify, timeout=timeout)
        log.info("Output received:\n{response}".format(response=response))

        return response

    @BaseConnection.locked
    def put(self,
            mount_point,
            payload,
            headers=None,
            timeout=30):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            mount_point (string): API url string
            payload (dict): payload dictionary
            headers (dict): Additional headers dictionary
            timeout: timeout in seconds (default: 30)
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        data_url = self.base_url
        full_url = '{url}/{mount_point}'.format(
            url=data_url,
            mount_point=mount_point)

        log.info("Sending PUT command to '{d}':"
                 "\nDN: {furl}".format(d=self.device.name, furl=full_url))

        if isinstance(payload, dict):
            payload = json.dumps(payload)

        hdr = self.default_headers

        if headers is not None:
            hdr.update(headers)

        response = self.session.put(full_url, data=payload, headers=hdr,
                                    verify=self.verify, timeout=timeout)
        log.info("Output received:\n{response}".format(response=response))

        return response

    @BaseConnection.locked
    def delete(self,
               mount_point,
               headers=None,
               timeout=30):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            mount_point (string): API url string
            payload (dict): payload dictionary
            headers (dict): Additional headers dictionary
            timeout: timeout in seconds (default: 30)
        '''
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))

        data_url = self.base_url
        full_url = '{url}/{mount_point}'.format(
            url=data_url,
            mount_point=mount_point)

        log.info("Sending DELETE command to '{d}':"
                 "\nDN: {furl}".format(d=self.device.name, furl=full_url))

        hdr = self.default_headers

        if headers is not None:
            hdr.update(headers)

        response = self.session.delete(full_url, headers=hdr,
                                       verify=self.verify, timeout=timeout)
        log.info("Output received:\n{response}".format(response=response))

        return response
