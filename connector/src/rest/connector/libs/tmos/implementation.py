# Global imports
import logging

# Genie, PyATS, ROBOT imports
from pyats.connections import BaseConnection
from rest.connector.utils import get_username_password

# F5 imports
from icontrol.session import iControlRESTSession
from icontrol.exceptions import iControlUnexpectedHTTPError

# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(BaseConnection):

    """Rest BaseClass



    Baseclass for Rest connection implementation



    YAML Example

    ------------



        devices:

            bigip1:
                type: 'generic'
                os: 'tmos'
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

    def __init__(self, *args, **kwargs):

        """__init__ instantiates a single connection instance."""

        # instanciate BaseConnection

        # (could use super...)

        BaseConnection.__init__(self, *args, **kwargs)

        self._is_connected = False

    @property
    def connected(self):

        """Is a device connected"""

        return self._is_connected

    def connect(self, *args, **kwargs):

        """connect to the device via REST"""

        username, password = get_username_password(self)
        icr_session = iControlRESTSession(username, password)
        payload = {"command": "run", "utilCmdArgs": '-c "runlevel"'}
        ip = self.connection_info["ip"].exploded
        port = self.connection_info.get("port", "443")
        self.base_url = "https://{ip}:{port}/".format(ip=ip, port=port)
        login_url = "{f}mgmt/tm/util/bash".format(f=self.base_url)

        log.info(
            "Connecting to '{d}' with alias "
            "'{a}'".format(d=self.device.name, a=self.alias)
        )

        # Connect to the device
        response = icr_session.post(login_url, json=payload)
        log.info(response)

        # Make sure it returned ok
        if not response.ok:
            # Something bad happened
            raise iControlUnexpectedHTTPError(
                "Connection to '{ip}' has returned the "
                "following code '{c}', instead of the "
                "expected status code 'ok'".format(
                    ip=ip, c=response.status_code
                )
            )

        self._is_connected = True
        log.info("Connected successfully to '{d}'".format(d=self.device.name))

        return self._is_connected

    def disconnect(self):

        """disconnect the device for this particular alias"""

        raise NotImplementedError

    def get(self, api_url, timeout=30, verbose=False):

        """GET REST Command to retrieve information from the device"""

        username, password = get_username_password(self)
        icr_session = iControlRESTSession(username, password)
        ip = self.connection_info["ip"].exploded
        port = self.connection_info.get("port", "443")
        self.base_url = "https://{ip}:{port}".format(ip=ip, port=port)

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        header = "Content-Type: application/json+{fmt}"

        log.info(
            "Sending GET to '{d}': "
            "{u}".format(d=self.device.name, u=full_url)
        )

        response = icr_session.get(full_url, timeout=timeout)

        output = response.json()

        log.debug(
            "Response: {c}, headers: {h}".format(
                c=response.status_code, h=header
            )
        )
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned ok
        if not response.ok:
            # Something bad happened
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

    def post(self, api_url, payload, timeout=30, verbose=False):
        """POST REST Command to configure information from the device"""

        if not self.connected:
            raise Exception(
                "'{d}' is not connected for "
                "alias '{a}'".format(d=self.device.name, a=self.alias)
            )

        username, password = get_username_password(self)
        icr_session = iControlRESTSession(username, password)
        ip = self.connection_info["ip"].exploded
        port = self.connection_info.get("port", "443")
        self.base_url = "https://{ip}:{port}".format(ip=ip, port=port)

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        header = "Content-Type: application/json+{fmt}"

        log.info(
            "Sending Post to '{d}': "
            "{u}"
            " with the header '{h}'"
            " and payload '{p}'".format(
                d=self.device.name, u=full_url, h=header, p=payload
            )
        )

        response = icr_session.post(full_url, json=payload, timeout=timeout)

        output = response.json()

        log.debug(
            "Response: {c}, headers: {h}".format(
                c=response.status_code, h=header
            )
        )
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned ok
        if not response.ok:
            # Something bad happened
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

    def put(self, api_url, payload, timeout=30, verbose=False):

        """PUT REST Command to update information on the device"""

        if not self.connected:
            raise Exception(
                "'{d}' is not connected for "
                "alias '{a}'".format(d=self.device.name, a=self.alias)
            )

        username, password = get_username_password(self)
        icr_session = iControlRESTSession(username, password)
        ip = self.connection_info["ip"].exploded
        port = self.connection_info.get("port", "443")
        self.base_url = "https://{ip}:{port}".format(ip=ip, port=port)

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        header = "Content-Type: application/json+{fmt}"

        log.info(
            "Sending Post to '{d}': "
            "{u}"
            " with the header '{h}'"
            " and payload '{p}'".format(
                d=self.device.name, u=full_url, h=header, p=payload
            )
        )

        response = icr_session.put(full_url, json=payload, timeout=timeout)

        output = response.json()

        log.debug(
            "Response: {c}, headers: {h}".format(
                c=response.status_code, h=header
            )
        )
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned ok
        if not response.ok:
            # Something bad happened
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

    def patch(self, api_url, payload, timeout=30, verbose=False):

        """PATCH REST Command to update information on the device"""

        if not self.connected:
            raise Exception(
                "'{d}' is not connected for "
                "alias '{a}'".format(d=self.device.name, a=self.alias)
            )

        username, password = get_username_password(self)
        icr_session = iControlRESTSession(username, password)
        ip = self.connection_info["ip"].exploded
        port = self.connection_info.get("port", "443")
        self.base_url = "https://{ip}:{port}".format(ip=ip, port=port)

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        header = "Content-Type: application/json+{fmt}"

        log.info(
            "Sending Post to '{d}': "
            "{u}"
            " with the header '{h}'"
            " and payload '{p}'".format(
                d=self.device.name, u=full_url, h=header, p=payload
            )
        )

        response = icr_session.patch(full_url, json=payload, timeout=timeout)

        output = response.json()

        log.debug(
            "Response: {c}, headers: {h}".format(
                c=response.status_code, h=header
            )
        )
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned ok
        if not response.ok:
            # Something bad happened
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

    def delete(self, api_url, timeout=30, verbose=False):

        """DELETE REST Command to delete information from the device"""

        if not self.connected:
            raise Exception(
                "'{d}' is not connected for "
                "alias '{a}'".format(d=self.device.name, a=self.alias)
            )

        username, password = get_username_password(self)
        icr_session = iControlRESTSession(username, password)
        ip = self.connection_info["ip"].exploded
        port = self.connection_info.get("port", "443")
        self.base_url = "https://{ip}:{port}".format(ip=ip, port=port)

        full_url = "{b}{a}".format(b=self.base_url, a=api_url)

        header = "Content-Type: application/json+{fmt}"

        log.info(
            "Sending Post to '{d}': "
            "{u}"
            " with the header '{h}'".format(
                d=self.device.name, u=full_url, h=header
            )
        )

        response = icr_session.delete(full_url, timeout=timeout)

        output = response.text

        log.debug(
            "Response: {c}, headers: {h}".format(
                c=response.status_code, h=header
            )
        )
        if verbose:
            log.info("Output received:\n{output}".format(output=output))

        # Make sure it returned ok
        if not response.ok:
            # Something bad happened
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
