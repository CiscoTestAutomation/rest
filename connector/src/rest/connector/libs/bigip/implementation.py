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

        try:
            log.info("Deleting token: '{t}'".format(t=self.token))
            delete_url = "https://{0}:{1}/mgmt/shared/authz/tokens/{2}".format(
                self.ip, self.port, self.token
            )

            delete_icr_session = iControlRESTSession(
                self.username,
                self.password,
                verify=self.verify,
                token_to_use=self.token
            )
            # Extending the timeout for the token received
            delete_icr_session.delete(delete_url)

            log.info("Token Deleted")

        finally:

            self._is_connected = False

        log.info(
            "'{t}' token deleted successfully.".format(t=self.token)
        )

    def isconnected(func):

        '''Decorator to make sure session to device is active



           There is limitation on the amount of time the session ca be active

           for on the NXOS devices. However, there are no way to verify if

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

    def connect(self, auth_provider='tmos', verify=False, *args, **kwargs):

        if self.connected:
            return

        self.username, self.password = get_username_password(self)
        self.ip = self.connection_info["ip"].exploded
        self.port = self.connection_info.get("port", "443")
        self.base_url = "https://{ip}:{port}".format(ip=self.ip, port=self.port)
        self.header = "Content-Type: application/json"
        self.verify = verify

        # URL to authenticate and receive the token
        url = "https://{0}:{1}/mgmt/shared/authn/login".format(
            self.ip, self.port
        )
        payload = {
            'username': self.username,
            'password': self.password,
            'loginProviderName': auth_provider
        }

        iCRS = iControlRESTSession(
            self.username,
            self.password,
            verify=self.verify
        )

        log.info(
            "Connecting to '{d}' with alias "
            "'{a}'".format(d=self.device.name, a=self.alias)
        )

        response = iCRS.post(
            url,
            json=payload,
        )

        log.info(response.json())

        if response.status_code not in [200]:
            if b'Configuration Utility restarting...' in response.content:
                time.sleep(30)
                # self.retries += 1
                return self.connect()
            else:
                # self.retries = 0
                return None, response.content

        self.token = response.json()['token']['token']

        log.info("The following toke is used to connect'{t}'".format(t=self.token))

        # Self-link of the token
        timeout_url = "https://{0}:{1}/mgmt/shared/authz/tokens/{2}".format(
            self.ip, self.port, self.token
        )
        timeout_payload = {"timeout": "3600"}

        token_icr_session = iControlRESTSession(
            self.username,
            self.password,
            verify=self.verify,
            token_to_use=self.token
        )

        # Extending the timeout for the token received
        token_icr_session.patch(timeout_url, json=timeout_payload)

        log.info("'{t}' - Token timeout extended to '{time}'".format(t=self.token, time=timeout_payload))

        params = dict(
            username=self.username,
            password=self.password,
            verify=self.verify,
            token_to_use=self.token
        )

        # creating an object to be used all new requests
        self.icr_session = iControlRESTSession(**params)

        self._is_connected = True

        log.info("Connected successfully to '{d}' using token: '{t}'".format(d=self.device.name, t=self.token))

        return self._is_connected, self.icr_session

    @isconnected
    def get(self, api_url, timeout=30, verbose=False):

        """GET REST Command to retrieve information from the device"""

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        log.info(
            "Sending GET to '{d}': "
            "{u}".format(d=self.device.name, u=full_url)
        )

        response = self.icr_session.get(full_url, timeout=timeout)

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

        log.info("Successfully fetched data using token: '{t}'".format(t=self.token))

        return output

    @BaseConnection.locked
    @isconnected
    def post(self, api_url, payload, timeout=30, verbose=False):
        """POST REST Command to configure information from the device"""

        if not self.connected:
            raise Exception(
                "'{d}' is not connected for "
                "alias '{a}'".format(d=self.device.name, a=self.alias)
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
                "'{d}' is not connected for "
                "alias '{a}'".format(d=self.device.name, a=self.alias)
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
                "'{d}' is not connected for "
                "alias '{a}'".format(d=self.device.name, a=self.alias)
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
                "'{d}' is not connected for "
                "alias '{a}'".format(d=self.device.name, a=self.alias)
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
