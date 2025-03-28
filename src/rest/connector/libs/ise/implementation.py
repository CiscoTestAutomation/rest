
import logging
import urllib.request
from requests.exceptions import RequestException

from pyats.connections import BaseConnection
from rest.connector.utils import get_username_password
from rest.connector.implementation import Implementation as RestImplementation

from ciscoisesdk import IdentityServicesEngineAPI

# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(RestImplementation):
    '''Rest Implementation for ISE

    Implementation of Rest connection to ISE servers

    YAML Example
    ------------

        devices:
            ise:
                os: ise
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

    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('topology.yaml')
        >>> device = testbed.devices['ise']
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
                verbose=False,
                port="443",
                protocol='https',
                debug=False,
                **kwargs):
        '''connect to the device via REST

        Arguments
        ---------

            timeout (int): Timeout value

        Raises
        ------

        Exception
        ---------

            If the connection did not go well

        '''
        if self.connected:
            log.info(f'{self} already connected')
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
            ip = self.connection_info.ip.exploded
            port = self.connection_info.get('port', port)

        if 'protocol' in self.connection_info:
            protocol = self.connection_info['protocol']

        self.base_url = '{protocol}://{ip}:{port}'.format(protocol=protocol,
                                                          ip=ip,
                                                          port=port)

        username, password = get_username_password(self)

        self.api = IdentityServicesEngineAPI(
            username=username, password=password,
            base_url=self.base_url, uses_api_gateway=True,
            verify=False, debug=debug)

        version_request = self.api.version_and_patch.get_ise_version_and_patch()
        if version_request.status_code == 200:
            version_info = version_request.response
            # {'OperationResult': {'resultValue': [
            # {'value': '3.3.0.430', 'name': 'version'}, {'value': '0', 'name': 'patch information'}]}}
            # Check if version_info is a dictionary
            if isinstance(version_info, dict):
                # Proceed with accessing the version information
                version_info_list = version_info.get('OperationResult', {}).get('resultValue', [])
            else:
                # Raise an appropriate error if version_info is not a dictionary
                raise TypeError(f"Expected version_info to be a dictionary, but received {version_info}")
            version_message_list = []
            for version_nv in version_info_list:
                name = version_nv.get('name')
                value = version_nv.get('value')
                if name and value:
                    version_message_list.append(f'{name}: {value}')
            if version_message_list:
                version_message = ' '.join(version_message_list)
                log.info(version_message)
            self._is_connected = True
            log.info("Connected successfully to '{d}'".format(d=self.device.name))
        else:
            raise ConnectionError('Unable to connect to ISE server')

        return self.api

    @BaseConnection.locked
    def disconnect(self):
        """
        """
        self._is_connected = False
        return
