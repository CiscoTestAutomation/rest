# Global imports
import logging
import time

# Genie, pyATS, ROBOT imports
# from pyats.connections import BaseConnection
from rest.connector.utils import get_username_password
from rest.connector.implementation import Implementation
from pyats.connections import BaseConnection

# F5 imports
from icontrol.session import iControlRESTSession
from icontrol.exceptions import iControlUnexpectedHTTPError

# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(Implementation):

    """Rest BaseClass



    Baseclass for Rest connection implementation



    YAML Example

    ------------



        devices:

            bigip1:
                type: 'generic'
                os: 'bigip'
                custom:
                    abstraction:
                        order: [os]
                connections:
                    # Console
                    a:
                        ip: 1.2.3.4
                        port: 22
                        protocol: ssh
                    rest:
                        # specify the rest connector class
                        class: rest.connector.Rest
                        ip: 1.2.3.4
                        port: "443"
                        protocol: https
                        credentials:
                            rest:
                                username: user
                                password: password



    Example

    -------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('/path/to/testbed.yaml')
        >>> device = testbed.devices['bigip1']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected

        True

    """

    @property
    def connected(self):

        """Is a device connected"""

        return self._is_connected

    def disconnect(self):
        """disconnect the device for this particular alias"""
        if self.token:
            try:
                log.info("Deleting token: '%s'", self.token)
                delete_url = (
                    f"{self.base_url}/mgmt/shared/authz/tokens/{self.token}"
                )

                delete_icr_session = iControlRESTSession(
                    self.username,
                    self.password,
                    verify=self.verify,
                    token_to_use=self.token
                )
                # Revoking the token received
                response = delete_icr_session.delete(delete_url)

                if not response.ok or response.status_code != 200:
                    log.error(
                        "Failed to delete session token for device %s",
                        self.device.name
                    )
                else:
                    log.info(
                        "Session token for device %s successfully deleted",
                        self.device.name
                    )
            finally:
                self.token = None
                self._is_connected = False

    def isconnected(func):
        '''Decorator to make sure the session to device is active.
        If the token experied, it will attempt to reconnect
        '''

        def decorated(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except iControlUnexpectedHTTPError as ex:
                # Auth failure - probably token expired
                if ex.response.status_code == 401:
                    log.info("Session with device %s expired", self.device.name)
                    log.info("Reconnecting to device %s", self.device.name)
                    self._is_connected = False
                    timeout = kwargs['timeout'] if 'timeout' in kwargs else 30
                    self._connect(timeout, retries=0, retry_wait=0)
                    result = func(self, *args, **kwargs)
                else:
                    raise
            return result
        return decorated

    def connect(
        self,
        auth_provider='tmos',
        verify=False,
        port='443',
        protocol='https',
        retries=3,
        retry_wait=10,
        timeout=30,
        ttl=3600,
        *args,
        **kwargs
    ):
        if self.connected:
            return

        # support sshtunnel
        if 'sshtunnel' in self.connection_info:
            try:
                from unicon.sshutils import sshtunnel
            except ImportError:
                raise ImportError(
                    "`unicon` is not installed for `sshtunnel`. "
                    "Please install by `pip install unicon`."
                )
            try:
                tunnel_port = sshtunnel.auto_tunnel_add(self.device, self.via)
                if tunnel_port:
                    self.ip = self.device.connections[self.via].sshtunnel.tunnel_ip
                    self.port = tunnel_port
            except AttributeError as e:
                raise AttributeError(
                    "Cannot add ssh tunnel. Connection %s may not have ip/host or port.\n%s"
                    % (self.via, e))
        else:
            self.ip = self.connection_info['ip'].exploded
            self.port = self.connection_info.get('port', port)

        if 'protocol' in self.connection_info:
            protocol = self.connection_info['protocol']

        self.base_url = '{protocol}://{ip}:{port}'.format(protocol=protocol,
                                                          ip=self.ip,
                                                          port=self.port)

        self.username, self.password = get_username_password(self)

        self.header = "Content-Type: application/json"
        self.verify = verify
        self._auth_provider = auth_provider
        self._ttl = ttl

        self._connect(timeout, retries, retry_wait)

        return self._is_connected, self.icr_session

    def _connect(self, timeout: int, retries: int, retry_wait: int):
        """ Authenticate and initiate a session with the device

        Args:
            timeout: The timeout to use when establishing the connection
            retries: How many times to retry to connect to the device if it fails
            retry_wait: Time in seconds to wait between retries
        """
        self._authenticate(timeout, retries, retry_wait)

        self._extend_session_ttl(self._ttl)

        params = dict(
            username=self.username,
            password=self.password,
            verify=self.verify,
            token_to_use=self.token
        )

        # creating an object to be used all new requests
        self.icr_session = iControlRESTSession(**params)

        self._is_connected = True

        log.info(
            "Connected successfully to '%s'", self.device.name
        )

    def _authenticate(self, timeout: int, retries: int, retry_wait: int):
        """ Authenticates with the device and retrieves a session token to be
            used in actual requests

        Args:
            timeout: The timeout to use when establishing the connection
            retries: How many times to retry to connect to the device if it fails
            retry_wait: Time in seconds to wait between retries
        """
        # URL to authenticate and receive the token
        url = f"{self.base_url}/mgmt/shared/authn/login"

        payload = {
            'username': self.username,
            'password': self.password,
            'loginProviderName': self._auth_provider
        }

        iCRS = iControlRESTSession(
            self.username,
            self.password,
            timeout=timeout,
            verify=self.verify
        )

        log.info(
            "Connecting to '%s'", self.device.name
        )

        response = iCRS.post(
            url,
            json=payload,
        )

        log.debug(response.json())

        if response.status_code != 200:
            if b'Configuration Utility restarting...' in response.content:
                if retries > 0:
                    time.sleep(retry_wait)
                    return self._authenticate(timeout, retries - 1, retry_wait)
                else:
                    raise iControlUnexpectedHTTPError(
                        f"Failed to connect to {self.device.name}: "
                        f"{response.content}"
                    )
            else:
                raise iControlUnexpectedHTTPError(
                    f"Failed to authenticate with {self.device.name}"
                )

        self.token = response.json()['token']['token']

        log.debug(
            "The following token is used to connect: '%s'", self.token
        )

    def _extend_session_ttl(self, ttl: int) -> None:
        """ Sets the TTL for the active session

        Args:
            ttl: The TTL to be set for the session
        """
        # Self-link of the token
        timeout_url = f"{self.base_url}/mgmt/shared/authz/tokens/{self.token}"
        timeout_payload = {"timeout": ttl}
        token_icr_session = iControlRESTSession(
            self.username,
            self.password,
            verify=self.verify,
            token_to_use=self.token
        )
        # Extending the timeout for the token received
        response = token_icr_session.patch(timeout_url, json=timeout_payload)
        if response.status_code != 200 or not response.ok:
            raise iControlUnexpectedHTTPError(
                "Failed to refresh session: "
                f"{response.reason} ({response.status_code})"
            )
        log.debug("Token TTL extended to '%d' seconds", ttl)

    @isconnected
    def get(self, api_url, timeout=30, verbose=False):

        """GET REST Command to retrieve information from the device"""

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        log.info(
            "Sending GET to '{d}': "
            "{u}".format(d=self.device.name, u=full_url)
        )

        response = self.icr_session.get(full_url, timeout=timeout)

        log.debug(
            "Response: {c}, headers: {h}".format(
                c=response.status_code, h=self.header
            )
        )
        if verbose:
            log.info("Output received:\n{output}".format(output=response))

        # Make sure it returned ok
        if not response.ok:
            raise iControlUnexpectedHTTPError(
                "Connection to '{d}' has returned the "
                "following code '{c}', instead of the "
                "expected status code 'ok'".format(
                    d=self.device.name, c=response.status_code
                )
            )

        log.info(
            "Successfully fetched data from '{d}'".format(d=self.device.name)
        )

        log.debug(
            "Successfully fetched data using token: '{t}'".format(t=self.token)
        )

        return response

    @BaseConnection.locked
    @isconnected
    def post(self, api_url, payload, timeout=30, verbose=False):
        """POST REST Command to configure information from the device"""

        if not self.connected:
            raise Exception(
                f"No active connection for '{self.device.name}'"
            )

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        log.info(
            "Sending Post to '{d}': "
            "{u}"
            " with the header '{h}'"
            " and payload '{p}'".format(
                d=self.device.name, u=full_url, h=self.header, p=payload
            )
        )

        response = self.icr_session.post(full_url, json=payload, timeout=timeout)

        output = response

        log.debug(
            "Response: {c}, headers: {h}".format(
                c=response.status_code, h=self.header
            )
        )
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned ok
        if not response.ok:
            raise iControlUnexpectedHTTPError(
                "Connection to '{d}' has returned the "
                "following code '{c}', instead of the "
                "expected status code 'ok'".format(
                    d=self.device.name, c=response.status_code
                )
            )

        log.info(
            "Successfully fetched data from '{d}'".format(d=self.device.name)
        )

        return output

    @BaseConnection.locked
    @isconnected
    def put(self, api_url, payload, timeout=30, verbose=False):

        """PUT REST Command to update information on the device"""

        if not self.connected:
            raise Exception(
                f"No active connection for '{self.device.name}'"
            )

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        log.info(
            "Sending Post to '{d}': "
            "{u}"
            " with the header '{h}'"
            " and payload '{p}'".format(
                d=self.device.name, u=full_url, h=self.header, p=payload
            )
        )

        response = self.icr_session.put(full_url, json=payload, timeout=timeout)

        output = response

        log.debug(
            "Response: {c}, headers: {h}".format(
                c=response.status_code, h=self.header
            )
        )
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned ok
        if not response.ok:
            raise iControlUnexpectedHTTPError(
                "Connection to '{d}' has returned the "
                "following code '{c}', instead of the "
                "expected status code 'ok'".format(
                    d=self.device.name, c=response.status_code
                )
            )

        log.info(
            "Successfully fetched data from '{d}'".format(d=self.device.name)
        )

        return output

    @BaseConnection.locked
    @isconnected
    def patch(self, api_url, payload, timeout=30, verbose=False):
        """PATCH REST Command to update information on the device"""

        if not self.connected:
            raise Exception(
                f"No active connection for '{self.device.name}'"
            )

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        log.info(
            "Sending Post to '{d}': "
            "{u}"
            " with the header '{h}'"
            " and payload '{p}'".format(
                d=self.device.name, u=full_url, h=self.header, p=payload
            )
        )

        response = self.icr_session.patch(full_url, json=payload, timeout=timeout)

        output = response

        log.debug(
            "Response: {c}, headers: {h}".format(
                c=response.status_code, h=self.header
            )
        )
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned ok
        if not response.ok:
            raise iControlUnexpectedHTTPError(
                "Connection to '{d}' has returned the "
                "following code '{c}', instead of the "
                "expected status code 'ok'".format(
                    d=self.device.name, c=response.status_code
                )
            )

        log.info(
            "Successfully fetched data from '{d}'".format(d=self.device.name)
        )

        return output

    @BaseConnection.locked
    @isconnected
    def delete(self, api_url, timeout=30, verbose=False):

        """DELETE REST Command to delete information from the device"""

        if not self.connected:
            raise Exception(
                f"No active connection for '{self.device.name}'"
            )

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        log.info(
            "Sending Post to '{d}': "
            "{u}"
            " with the header '{h}'".format(
                d=self.device.name, u=full_url, h=self.header
            )
        )

        response = self.icr_session.delete(full_url, timeout=timeout)

        output = response.text

        log.debug(
            "Response: {c}, headers: {h}".format(
                c=response.status_code, h=self.header
            )
        )
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned ok
        if not response.ok:
            raise iControlUnexpectedHTTPError(
                "Connection to '{d}' has returned the "
                "following code '{c}', instead of the "
                "expected status code 'ok'".format(
                    d=self.device.name, c=response.status_code
                )
            )

        log.info(
            "Successfully fetched data from '{d}'".format(d=self.device.name)
        )

        return output

    def configure(self, *args, **kwargs):

        """configure - Not implemented for REST"""

        raise NotImplementedError(
            "configure is not a supported method for REST. "
            "post is probably what you are looking for"
        )

    def execute(self, *args, **kwargs):

        """execute - Not implemented for REST"""

        raise NotImplementedError(
            "execute is not a supported method for REST. "
            "get is probably what you are looking for."
        )
