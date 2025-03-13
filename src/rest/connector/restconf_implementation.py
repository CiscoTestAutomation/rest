"""
The RestconfImplementation class provides a common interface for
implementations using the RESTCONF protocol (RFC8040) code duplication.

To subclass, inherit
"""

from logging import getLogger
from typing import Optional, Union
from json import dumps as json_dumps
from ipaddress import ip_address, IPv6Address

from urllib.request import getproxies as urllib_getproxies
from urllib.parse import urljoin
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from dict2xml import dict2xml

from pyats.connections import BaseConnection
from rest.connector.implementation import Implementation
from rest.connector.utils import default_response_hook

from requests import (codes as requests_codes,
                      Response as requests_Response,
                      Session as requests_Session,)
from requests.exceptions import RequestException

log = getLogger(__name__)

# Default timeout
DEFAULT_REQUEST_TIMEOUT = 30

# Default status codes per RFC for each HTTP method.
DEFAULT_STATUS_CODES = {
    "OPTIONS": (requests_codes.ok,),
    "HEAD": (requests_codes.no_content,
             requests_codes.ok,),
    "GET": (requests_codes.no_content,
            requests_codes.ok,),
    "POST": (requests_codes.created,
             requests_codes.no_content,
             requests_codes.ok,),
    "PATCH": (requests_codes.no_content,
              requests_codes.ok,),
    "PUT": (requests_codes.created,
            requests_codes.no_content,),
    "DELETE": (requests_codes.no_content,),
}


class RestconfImplementation(Implementation):
    '''RESTCONF Implementation BaseClass

    Baseclass for Rest connection implementation

    YAML Example
    ------------

        devices:
          PE1:
            credentials:
              rest:
                username: admin
                password: cisco123
            connections:
              a:
                protocol: telnet
                ip: "1.2.3.4"
                port: 2004
              vty:
                protocol : telnet
                ip : "2.3.4.5"
              rest:
                class: rest.connector.Rest
                host: device.example.com
                port: "443"
                protocol: https
                verify: true
                credentials:
                  rest:
                    username: admin
                    password: cisco123

    Example
    -------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('/users/xxx/xxx/asr22.yaml')
        >>> device = testbed.devices['PE1']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected
        True
    '''
    def __init__(self, *args, **kwargs):
        '''__init__ instantiates a single connection instance.'''

        # instantiate BaseConnection
        super().__init__(*args, **kwargs)

        self._is_connected = False
        self.protocol = self.connection_info.get("protocol", "https")
        self.port = self.connection_info.get("port", 443)

        self.host = self.connection_info.get("host", self.connection_info.get("ip"))

        if "proxies" in kwargs:
            self.proxies = kwargs["proxies"]
        elif hasattr(self.connection_info, "proxies"):
            self.proxies = self.connection_info.get("proxies")
        else:
            self.proxies = urllib_getproxies()

        if self.host is None:
            raise AttributeError(
                "Cannot connect to device. "
                f"Connection {self.via} may not have host/ip defined."
            )

        # support sshtunnel
        if 'sshtunnel' in self.connection_info:
            try:
                from unicon.sshutils import sshtunnel
            except ImportError as e:
                raise ImportError(
                    "`unicon` is not installed for `sshtunnel`. "
                    "Please install by `pip install unicon`."
                ) from e
            try:
                tunnel_port = sshtunnel.auto_tunnel_add(self.device, self.via)
                if tunnel_port:
                    self.host = self.device.connections[self.via].sshtunnel.tunnel_ip
                    self.port = tunnel_port
            except AttributeError as e:
                raise AttributeError(
                    f"Cannot add ssh tunnel. Connection {self.via} may not have ip/host or port.\n{e}"
                ) from e


        try:
            # If IPv6 address provided, format for proper URL
            self.host = ip_address(self.host)
            if isinstance(self.host, IPv6Address):
                self.host = f"[{self.host.exploded}]"
            else:
                self.host = self.host.exploded
        except ValueError:
            # Hostname provided (not IP) - leave as-is
            pass

        self.url = f"{self.protocol}://{self.host}:{self.port}/"

        # Create and configure the Session instance
        self.session = requests_Session()

        self.session.verify = self.connection_info.get("verify", True)
        if self.session.verify:
            # remove warnings for insecure HTTPS
            disable_warnings(InsecureRequestWarning)

        self.session.timeout = DEFAULT_REQUEST_TIMEOUT
        self.session.proxies.update(self.proxies)

        # Attach a default response hook to raise for status and re-raise
        # caught exceptions
        self.session.hooks["response"] = [default_response_hook]

    @BaseConnection.locked
    def _request(self,
                method: str,
                url: str,
                content_type: Optional[str] = None,
                message_body: Union[dict, str, None] = None,
                headers: Optional[dict] = None,
                timeout: Optional[int] = None,
                expected_status_codes: Union[list, set, tuple] = None,
                verbose: Optional[bool] = False) -> requests_Response:
        """
        Handle sending the request to the device and validating the response.
        If successful, return the response object.

        :param method: HTTP method (verb) for the request
        :param url: Relative URL of the resource to be joined to the base URL
        :param content_type: Optional - override the content type
        :param message_body: RESTCONF message body to send
        :param headers: Optional - override the default headers
        :param timeout: Optional - override the default timeout
        :param expected_status_codes: Optional - override the expected status codes
        :param verbose: Enable additional information about the request
        :return: Response object
        :raises: None
        """
        if not self.connected:
            # TODO: Consider more specific or pyATS-specific exception
            raise Exception(f"'{self.device.name}' is not connected for alias '{self.alias}'")

        # Set the content-type
        header = 'application/yang-data+{fmt}'
        content_type = (content_type or self.content_type).lower()
        if content_type.lower() in ("json", "xml"):
            accept_header = header.format(fmt=content_type)
        else:
            accept_header = content_type

        self.session.headers.update(
            {
                "Content-Type": accept_header,
                "Accept": accept_header
            }
        )

        # Encode the message body for json | xml. Otherwise, leave as-is
        if message_body is not None:
            if content_type.lower() == "json":
                message_body = json_dumps(message_body)
            elif content_type.lower() == "xml" and isinstance(message_body, dict):
                message_body = dict2xml(message_body)

        # Add any additional headers, but don't update the session headers
        if headers is not None:
            request_headers = self.session.headers.copy()
            request_headers.update(headers)
        else:
            request_headers = self.session.headers

        # Use session timeout if not provided per-request
        if timeout is None:
            timeout = self.session.timeout

        # Default expected status codes, if not provided for the request
        if expected_status_codes is None:
            expected_status_codes = DEFAULT_STATUS_CODES[method.upper()]

        # Complete the URL
        resource_url = urljoin(self.base_url, url)

        log.debug("Sending %s command to '%s': %s", method, self.device.name, url)
        log.debug("Request headers: %s", self.session.headers)
        log.debug("Request timeout: %s", timeout)
        log.debug("Valid status codes: %s", expected_status_codes)
        if message_body is not None:
            log.debug("Message body: %s", message_body)

        # All other request parameters are handled in the Session object
        response = self.session.request(method,
                                        resource_url,
                                        data=message_body,
                                        headers=request_headers,
                                        timeout=timeout)

        output = response.text
        log.debug("Response: %s %s, headers: %s",
                  response.status_code,
                  response.reason,
                  response.headers)
        if verbose:
            log.info("Output received:\n%s", output)

        # Make sure it returned requests.codes.ok
        if response.status_code not in expected_status_codes:
            # Something bad happened
            # TODO - custom exception class?
            raise RequestException(f"'{response.status_code}' result code has been returned "
                                   f"instead of the expected status code(s) "
                                   f"'{expected_status_codes}' for "
                                   f"'{self.device.name}'\n{response.text}")
        return response
