from json import dumps as json_dumps
from logging import getLogger
from typing import Optional, Union

from urllib.parse import urljoin
from requests import (codes as requests_codes,
                      Response as requests_Response)
from requests.exceptions import RequestException

from pyats.connections import BaseConnection
from rest.connector.restconf_implementation import RestconfImplementation
from rest.connector.utils import get_username_password

# create a logger for this module
log = getLogger(__name__)


class Implementation(RestconfImplementation):
    '''Rest Implementation for IOS-XE

    Implementation of Rest connection to IOS-XE devices supporting RESTCONF

    YAML Example
    ------------

        devices:
            eWLC:
                os: iosxe
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
                custom:
                    abstraction:
                        order: [os]

    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('topology.yaml')
        >>> device = testbed.devices['eWLC']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected
        True
    '''

    def __init__(self, *args, **kwargs):
        """
        Prepare the object for consupmption and define any attributes not
        explicitly set in the super() call.

        :param args: Arguments
        :param kwargs: Keyword Arguments
        """
        super().__init__(*args, **kwargs)
        self.base_url = self.url
        self.content_type = None

    @BaseConnection.locked
    def connect(self,
                timeout: Optional[int] = None,
                default_content_type: str = "json",
                verbose: bool = False,
                port: Union[int, str, None] = 443,           # Legacy - port defined in testbed
                protocol: Optional[str] = "https") -> None:  # Legacy - protocol defined in testbed
        '''connect to the device via REST

        Arguments
        ---------

            timeout: (int) Timeout value
            default_content_type: (str: json|xml) Default for content type, json or xml
            verbose: (bool) Display more detail about the connection
            proxies: Specify the proxy to use for connection as seen below.
                    {'http': 'http://proxy.esl.cisco.com:80/',
                    'ftp': 'http://proxy.esl.cisco.com:80/',
                    'https': 'http://proxy.esl.cisco.com:80/',
                    'no': '.cisco.com'}

        Raises
        ------

        Exception
        ---------

            If the connection did not go well

        Note
        ----

        Connecting via RESTCONF does not require contacting the device.
        This does nothing

        '''
        if self.connected:
            return

        log.debug("Content type: %s", default_content_type)
        log.debug("Timeout: %s", timeout)

        # ---------------------------------------------------------------------
        # Connect to "well-known" RESTCONF resource to "test", the
        # RESTCONF connection on 'connect'. Comparable to CLI (SSH) connection,
        # which triggers a "show version" on connect
        # ---------------------------------------------------------------------
        log.info("Connecting to '%s' with alias '%s'",
                 self.device.name,
                 self.alias)

        login_url = urljoin(self.base_url,
                            "/restconf/data/Cisco-IOS-XE-native:native/version")

        username, password = get_username_password(self)
        self.session.auth = (username, password)

        self.content_type = default_content_type

        if timeout is not None:
            self.session.timeout = timeout

        # Connect to the device directly via requests and set the connected
        # flag on success.

        # NOTE - all session attribute already set in __init__
        # (proxies, verify, etc)
        response = self.session.get(login_url)
        output = response.text
        log.debug("Response: %s %s, headers: %s, payload %s",
                  response.status_code,
                  response.reason,
                  response.headers,
                  response.text)
        if verbose:
            log.info("Response text:\n%s", output)

        # Make sure it returned requests.codes.ok
        if response.status_code != requests_codes.ok:
            # Something bad happened
            # TODO - Custom exception class?
            raise RequestException(f"Connection to '{self.host}:{self.port}' has returned the "  # self.url???
                                   f"following code '{response.status_code}', instead of the "
                                   f"expected status code '{requests_codes.ok}'")

        self._is_connected = True
        log.info("Connected successfully to '%s'", self.device.name)

    @BaseConnection.locked
    def disconnect(self):
        """
            Does not make sense to disconnect from a device.
        """

        log.info("Disconnecting from '%s' with alias '%s'",
                 self.device.name, self.alias)
        try:
            self.session.close()
        finally:
            self._is_connected = False

        log.info("Disconnected successfully from '%s'",
                 self.device.name)

    @BaseConnection.locked
    def options(self,
                api_url: str,
                content_type: Optional[str] = None,
                headers: Optional[dict] = None,
                expected_status_codes: Union[list[int], set[int], tuple[int], None] = None,
                timeout: Optional[int] = None,
                verbose: Optional[bool] = False) -> requests_Response:
        '''OPTIONS REST Command to retrieve supported methods from device

        Arguments
        ---------
        api_url: API url string
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        verbose: Enable additional information in output (default: False)
        '''
        return self._request(method="OPTIONS",
                             url=api_url,
                             content_type=content_type,
                             expected_status_codes=expected_status_codes,
                             verbose=verbose,
                             timeout=timeout)

    @BaseConnection.locked
    def head(self,
             api_url: str,
             content_type: Optional[str] = None,
             headers: Optional[dict] = None,
             expected_status_codes: Union[list[int], set[int], tuple[int], None] = None,
             timeout: Optional[int] = None,
             verbose: Optional[bool] = False) -> requests_Response:
        '''OPTIONS REST Command to retrieve resource metadata via headers

        Arguments
        ---------
        api_url: API url string
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        verbose: Enable additional information in output (default: False)
        '''
        return self._request(method="HEAD",
                             url=api_url,
                             content_type=content_type,
                             expected_status_codes=expected_status_codes,
                             verbose=verbose,
                             timeout=timeout)

    @BaseConnection.locked
    def get(self,
            api_url: str,
            content_type: Optional[str] = None,
            headers: Optional[dict] = None,
            expected_status_codes: Union[list[int], set[int], tuple[int], None] = None,
            timeout: Optional[int] = None,
            verbose: Optional[bool] = False) -> requests_Response:
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------
        api_url: API url string
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        verbose: Enable additional information in output (default: False)
        '''
        return self._request(method="GET",
                             url=api_url,
                             content_type=content_type,
                             headers=headers,
                             expected_status_codes=expected_status_codes,
                             verbose=verbose,
                             timeout=timeout)

    @BaseConnection.locked
    def post(self,
             api_url: str,
             payload: Union[dict, str],
             content_type: Optional[str] = None,
             headers: Optional[dict] = None,
             expected_status_codes: Union[list[int], set[int], tuple[int], None] = None,
             timeout: Optional[int] = None,
             verbose: Optional[bool] = False) -> requests_Response:
        '''POST REST Command to configure information from the device

        Arguments
        ---------
        api_url: API url string
        payload: payload to sent, can be string or dict
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        verbose: Enable additional information in output (default: False)
        '''
        return self._request(method="POST",
                             url=api_url,
                             content_type=content_type,
                             message_body=payload,
                             headers=headers,
                             expected_status_codes=expected_status_codes,
                             verbose=verbose,
                             timeout=timeout)

    @BaseConnection.locked
    def patch(self,
              api_url: str,
              payload: Union[dict, str],  # , None] = None,
              content_type: Optional[str] = None,
              headers: Optional[dict] = None,
              expected_status_codes: Union[list[int], set[int], tuple[int], None] = None,
              timeout: Optional[int] = None,
              verbose: Optional[bool] = False) -> requests_Response:
        '''PATCH REST Command to configure information from the device

        Arguments
        ---------
        api_url: API url string
        payload: payload to sent, can be string or dict
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        verbose: Enable additional information in output (default: False)
        '''
        return self._request(method="PATCH",
                             url=api_url,
                             content_type=content_type,
                             message_body=payload,
                             headers=headers,
                             expected_status_codes=expected_status_codes,
                             verbose=verbose,
                             timeout=timeout)

    @BaseConnection.locked
    def put(self,
            api_url: str,
            payload: Union[dict, str],  # , None] = None,
            content_type: Optional[str] = None,
            headers: Optional[dict] = None,
            expected_status_codes: Union[list[int], set[int], tuple[int], None] = None,
            timeout: Optional[int] = None,
            verbose: Optional[bool] = False) -> requests_Response:
        '''PUT REST Command to configure information from the device

        Arguments
        ---------
        api_url: API url string
        payload: payload to sent, can be string or dict
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        verbose: Enable additional information in output (default: False)
        '''
        return self._request(method="PUT",
                             url=api_url,
                             content_type=content_type,
                             message_body=payload,
                             headers=headers,
                             expected_status_codes=expected_status_codes,
                             verbose=verbose,
                             timeout=timeout)

    @BaseConnection.locked
    def delete(self,
               api_url: str,
               content_type: Optional[str] = None,
               headers: Optional[dict] = None,
               expected_status_codes: Union[list[int], set[int], tuple[int], None] = None,
               timeout: Optional[int] = None,
               verbose: Optional[bool] = False) -> requests_Response:
        '''DELETE REST Command to configure information from the device

        Arguments
        ---------
        api_url: API url string
        content_type: expected content type to be returned (xml or json)
        headers: dictionary of HTTP headers (optional)
        expected_status_codes: list of expected result codes (integers)
        timeout: timeout in seconds (default: 30)
        verbose: Enable additional information in output (default: False)
        '''
        return self._request(method="DELETE",
                             url=api_url,
                             content_type=content_type,
                             headers=headers,
                             expected_status_codes=expected_status_codes,
                             verbose=verbose,
                             timeout=timeout)
