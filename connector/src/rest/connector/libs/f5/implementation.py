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

        username, password = get_username_password(self)
        icr_session = iControlRESTSession(username, password)
        payload = {"command": "run", "utilCmdArgs": '-c "runlevel"'}
        ip = self.connection_info["ip"].exploded
        self.url = "https://{ip}/".format(ip=ip)
        login_url = "{f}mgmt/tm/util/bash".format(f=self.url)

        log.info(
            "Connecting to '{d}' with alias "
            "'{a}'".format(d=self.device.name, a=self.alias)
        )

        # Connect to the device
        response = icr_session.post(self.url + login_url, json=payload)
        log.info(response)

        # Make sure it returned ok
        if not response.ok:
            # Something bad happened
            raise iControlUnexpectedHTTPError(
                "Connection to '{ip}' has returned the "
                "following code '{c}', instead of the "
                "expected status code 'ok'".format(ip=ip, c=response.status_code)
            )
        self._is_connected = True
        log.info("Connected successfully to '{d}'".format(d=self.device.name))

        return self._is_connected

    def connect(self, *args, **kwargs):

        """connect to the device via REST"""

        raise NotImplementedError

    def disconnect(self):

        """disconnect the device for this particular alias"""

        raise NotImplementedError

    def get(self, *args, **kwargs):

        """GET REST Command to retrieve information from the device"""

        raise NotImplementedError

    def post(self, *args, **kwargs):

        """POST REST Command to configure information from the device"""

        raise NotImplementedError

    def put(self, *args, **kwargs):

        """PUT REST Command to update information on the device"""

        raise NotImplementedError

    def patch(self, *args, **kwargs):

        """PATCH REST Command to update information on the device"""

        raise NotImplementedError

    def delete(self, *args, **kwargs):

        """DELETE REST Command to delete information from the device"""

        raise NotImplementedError

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
