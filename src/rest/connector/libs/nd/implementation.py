import json
import logging
import requests
import time
import urllib.parse

from requests.exceptions import RequestException

from pyats.connections import BaseConnection
from rest.connector.implementation import Implementation as Imp
from rest.connector.utils import get_username_password

# create a logger for this module
log = logging.getLogger(__name__)


class Implementation(Imp):
    """Rest Implementation for ND
    Implementation of Rest connection to devices based on pyATS BaseConnection
    for ND

    YAML Example
    ------------

        devices:
            nd1:
                os: nd
                connections:
                    rest:
                        class: rest.connector.Rest
                        ip : "2.3.4.5"
                credentials:
                    rest:
                        username: admin
                        password: [REDACT]

    Code Example
    ------------
        >>> from pyats.topology import loader
        >>> testbed = loader.load('/users/xxx/xxx/testbed.yaml')
        >>> device = testbed.devices['nd1']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected
        True
    """

    @BaseConnection.locked
    def connect(self, timeout=30, retries=3, retry_wait=10, verify=False):
        """connect to the device via REST
        Arguments
        ---------
            timeout (int): Timeout value
            retries (int): Max retries on request exception (default: 3)
            retry_wait (int): Seconds to wait before retry (default: 10)
            verify (bool): defaults to False

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
                nd1:
                    os: nd
                    connections:
                        rest:
                            class: rest.connector.Rest
                            ip : "2.3.4.5"
                    credentials:
                        rest:
                            username: admin
                            password: [REDACT]
                            domain: 'DefaultAuth'   # this is optional if domain is not specified 'DefaultAuth' becomes default value


        Code Example
        ------------
            >>> from pyats.topology import loader
            >>> testbed = loader.load('/users/xxx/xxx/testbed.yaml')
            >>> device = testbed.devices['nd1']
            >>> device.connect(alias='rest', via='rest')
        """

        if self.connected:
            return

        if 'host' in self.connection_info:
            ip = self.connection_info['host']
        else:
            ip = self.connection_info['ip'].exploded
        if 'port' in self.connection_info:
            port = self.connection_info['port']
            self.url = f'https://{ip}:{port}/'
        else:
            self.url = f'https://{ip}/'
        self.verify = verify
        login_url = f'{self.url}login'

        username, password = get_username_password(self)
        domain = str(self.connection_info['credentials']['rest'].get('domain','DefaultAuth'))

        payload = {
            "userName": username,
            "userPasswd": password,
            "domain": domain
        }

        headers = {
            'Content-Type': 'application/json'
        }

        log.info("Connecting to '{d}' with alias "
                 "'{a}'".format(d=self.device.name, a=self.alias))

        self.session = requests.Session()
        _data = json.dumps(payload)

        for _ in range(retries):
            try:
                # Connect to the device via requests
                response = self.session.post(login_url, data=_data, timeout=timeout,
                                             verify=False, headers=headers)
                log.info(response)

                # Make sure it returned requests.codes.ok
                if response.status_code != requests.codes.ok:
                    # Something bad happened
                    raise RequestException(f"Connection to '{ip}' has returned the "
                                           f"following code '{response.status_code}', instead of the "
                                           f"expected status code '{requests.codes.ok}'")
                break
            except Exception:
                log.warning(f'Request to {self.device.name} failed. Waiting {retry_wait} seconds before retrying\n',
                            exc_info=True)
                time.sleep(retry_wait)
        else:
            raise ConnectionError(f'Connection to {self.device.name} failed')

        self._is_connected = True
        log.info(f"Connected successfully to '{self.device.name}'")

    @BaseConnection.locked
    def disconnect(self):
        """disconnect the device for this particular alias"""

        log.info(f"Disconnecting from '{self.device.name}' with "
                 f"alias '{self.alias}'")
        try:
            self.session.close()
        finally:
            self._is_connected = False
        log.info(f"Disconnected successfully from "
                 "'{self.device.name}'")

    def isconnected(func):
        """Decorator to make sure session to device is active

           There is limitation on the amount of time the session can be active
           on the ND. However, there is no way to verify if
           session is still active unless sending a command. So, it's just
           faster to reconnect every time.
         """

        def decorated(self, *args, **kwargs):
            try:
                ret = func(self, *args, **kwargs)
            except:
                self.disconnect()

                if 'timeout' in kwargs:
                    self.connect(timeout=kwargs['timeout'])
                else:
                    self.connect()

                ret = func(self, *args, **kwargs)
            return ret

        return decorated

    @BaseConnection.locked
    @isconnected
    def get(self, api_url, expected_status_code=requests.codes.ok,
            timeout=30, retries=3, retry_wait=10, params=None):
        """GET REST Command to retrieve information from the device
        Arguments
        ---------
            api_url (string): subdirectory part of the API URL
            expected_status_code (int): Expected result
            timeout (int): Maximum time
            retries (int): Number of retries in case of transmission error
            retry_wait (int): Seconds to wait between retries
        """

        if not self.connected:
            raise Exception(f"'{self.device.name}' is not connected for "
                            f"alias '{self.alias}'")
        #Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = f"{self.url}{api_url}"

        log.info(f"Sending GET command to '{self.device.name}':" \
                 f"\nURL: {full_url}")

        for _ in range(retries):
            try:
                if params:
                    response = self.session.get(full_url, params=params, timeout=timeout, verify=self.verify)
                else:
                    response = self.session.get(full_url, timeout=timeout, verify=self.verify)
                break
            except Exception:
                log.warning(f'Request to {self.device.name} failed. '
                            f'Waiting {retry_wait} seconds before retrying\n'
                            , exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException(f'Sending "{full_url}" to "{self.device.name}" has failed '
                                   f'after {retries} tries')

        try:
            output = response.json() # Response need not be always in json
            log.info(f"Output received:\n{json.dumps(output, indent=2, sort_keys=True)}")
        except Exception:
            output = response.text
            log.info(f"Output received: {output}")

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException(f"GET {full_url} to {self.device.name} has returned the following code "
                                   f"{response.status_code}, instead of the expected status code "
                                   f"'{expected_status_code}', got {response.text}")
        return output

    @BaseConnection.locked
    @isconnected
    def post(self, api_url, payload, expected_status_code=requests.codes.ok,
             content_type='json', timeout=30, retries=3, retry_wait=10):
        """POST REST Command to configure information from the device
        Arguments
        ---------
            api_url (string): subdirectory part of the API URL
            payload (dict|string): Information to send via the post
            expected_status_code (int): Expected result
            content_type(string): json / xml / form
            timeout (int): Maximum time
        """

        if not self.connected:
            raise Exception(f"'{self.device.name}' is not connected for "
                            f"alias '{self.alias}'")
        # Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = f'{self.url}{api_url}'

        log.info(f"Sending POST command to '{self.device.name}':" \
                 f"\nURL: {full_url}\nPayload:{payload}")
        headers = {'form': 'application/x-www-form-urlencoded',
                   'json': 'application/json',
                   'xml': 'application/xml'}

        if content_type == 'form' and isinstance(payload, dict):
            payload = urllib.parse.urlencode(payload, safe=':!')
        elif content_type == 'xml':
            if isinstance(payload, dict):
                raise ValueError(f"Error on {self.device.name} during POST command: "
                                 "Payload needs to be string in xml format if used "
                                 "in conjunction with content_type='xml' argument")

        for _ in range(retries):
            try:
                # Send to the device
                if isinstance(payload, dict):
                    response = self.session.post(full_url, json=payload, timeout=timeout,
                                                 verify=False)
                else:
                    response = self.session.post(full_url, data=payload, timeout=timeout,
                                                 verify=False,
                                                 headers={'Content-type': headers.get(content_type,
                                                                                      headers['json'])})
                break
            except Exception:
                log.warning(f'Request to {self.device.name} failed. Waiting {retry_wait} seconds before retrying\n'
                            , exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException(f'Sending "{full_url}" to "{self.device.name}" has failed '
                                   f'after {retries} tries')

        try:
            # response might not pe in JSON format
            output = response.json()
            log.info(f"Output received:\n{output}")
        except Exception:
            output = response.content if content_type == 'xml' else response.text
            log.info(f"'Post' operation did not return a json response: {output}")

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException(f"POST {full_url} to {self.device.name} has returned the "
                                   f"following code '{response.status_code}', instead of the "
                                   f"expected status code '{expected_status_code}'"
                                   f", got:\n {response.text}")
        return output

    @BaseConnection.locked
    @isconnected
    def post(self, api_url, params=None, data=None, json=None, files=None,
             timeout=30, retries=3, retry_wait=10) -> requests.Response:
        """POST REST Command to configure information from the device
        Arguments
        ---------
            api_url (string): subdirectory part of the API URL
            params (dict): Query string parameters
            data (dict):
            json (json) : if request header Content-Type is application/json
            files (dict):
            expected_status_code (int): Expected result
            timeout (int): Maximum time
        """

        if not self.connected:
            raise Exception(f"'{self.device.name}' is not connected for "
                            f"alias '{self.alias}'")
        # Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = f'{self.url}{api_url}'

        for _ in range(retries):
            try:
                if params and not json:
                    response = self.session.post(full_url, params=params, timeout=timeout,
                                                verify=self.verify)
                elif params and json:
                    response = self.session.post(full_url,params=params, json=json,
                                                 timeout=timeout, verify=self.verify)
                elif json and not params:
                    response = self.session.post(full_url,json=json,
                                                 timeout=timeout, verify=self.verify)
                elif data:
                    response = self.session.post(full_url, data=data,
                                                 timeout=timeout, verify=self.verify)
                elif files:
                    response = self.session.post(full_url, files=files,
                                                 timeout=timeout, verify=self.verify)
                else:
                    response = self.session.post(full_url, timeout=timeout, verify=self.verify)

                break
            except Exception:
                log.warning(f'Request to {self.device.name} failed. '
                            f'Waiting {retry_wait} seconds before retrying\n'
                            , exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException(f'Sending "{full_url}" to "{self.device.name}" has failed '
                                   f'after {retries} tries')

        return response

    @BaseConnection.locked
    @isconnected
    def put(self, api_url, payload=None, expected_status_code=requests.codes.ok,
            content_type='json', timeout=30, retries=3, retry_wait=10):
        """PUT REST Command to configure information from the device
        Arguments
        ---------
            api_url (string): subdirectory part of the API URL
            payload (dict|string): Information to send via the put action
            expected_status_code (int): Expected result
            content_type(string): json / xml / form
            timeout (int): Maximum time
        """

        if not self.connected:
            raise Exception(f"'{self.device.name}' is not connected for "
                           f"alias '{self.alias}'")
        # Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = f'{self.url}{api_url}'

        log.info(f"Sending PUT command to '{self.device.name}':" \
                 f"\nURL: {full_url}\nPayload:{payload}")
        headers = {'form': 'application/x-www-form-urlencoded',
                   'json': 'application/json',
                   'xml': 'application/xml'}

        if content_type == 'form' and isinstance(payload, dict):
            payload = urllib.parse.urlencode(payload, safe=':!')
        elif content_type == 'xml':
            if isinstance(payload, dict):
                raise ValueError(f"Error on {self.device.name} during PUT command: "
                                 f"Payload must to be string in xml format if used "
                                 f"in conjunction with content_type='xml' argument")

        for _ in range(retries):
            try:
                # Send to the device
                if isinstance(payload, dict):
                    response = self.session.put(full_url, json=payload, timeout=timeout,
                                                verify=False)
                else:
                    response = self.session.put(full_url, data=payload, timeout=timeout,
                                                verify=False,
                                                headers={'Content-type': headers.get(content_type,
                                                                                     headers['json'])})
                break
            except Exception:
                log.warning(f'Request to {self.device.name} failed. Waiting {retry_wait} seconds before retrying\n'
                            , exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException(f'Sending "{full_url}" to "{self.device.name}" has failed '
                                   f'after {retries} tries')

        try:
            # response might not pe in JSON format
            output = response.json()
            log.info(f"Output received:\n{output}")
        except Exception:
            output = response.content if content_type == 'xml' else response.text
            log.info(f"'Put' operation did not return a json response: {output}")

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException(f"PUT {full_url} to {self.device.name} has returned the "
                                   f"following code '{response.status_code}', instead of the "
                                   f"expected status code '{expected_status_code}'"
                                   f", got:\n {response.text}")
        return output

    @BaseConnection.locked
    @isconnected
    def put(self, api_url, params=None, data=None, json=None, files=None,
             timeout=30, retries=3, retry_wait=10) -> requests.Response:
        """PUT REST Command to configure information from the device
        Arguments
        ---------
            api_url (string): subdirectory part of the API URL
            params (dict): Query string parameters
            data (dict):
            json (json) : if request header Content-Type is application/json
            files (dict):
            expected_status_code (int): Expected result
            timeout (int): Maximum time
        """

        if not self.connected:
            raise Exception(f"'{self.device.name}' is not connected for "
                            f"alias '{self.alias}'")
        # Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = f'{self.url}{api_url}'

        for _ in range(retries):
            try:
                if params and not json:
                    response = self.session.put(full_url, params=params, timeout=timeout,
                                                 verify=self.verify)
                elif params and json:
                    response = self.session.put(full_url, params=params, json=json,
                                                 timeout=timeout, verify=self.verify)
                elif json and not params:
                    response = self.session.put(full_url, json=json,
                                                 timeout=timeout, verify=self.verify)
                elif data:
                    response = self.session.put(full_url, data=data,
                                                 timeout=timeout, verify=self.verify)
                elif files:
                    response = self.session.put(full_url, files=files,
                                                 timeout=timeout, verify=self.verify)
                else:
                    response = self.session.put(full_url, timeout=timeout, verify=self.verify)

                break
            except Exception:
                log.warning(f'Request to {self.device.name} failed. '
                            f'Waiting {retry_wait} seconds before retrying\n'
                            , exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException(f'Sending "{full_url}" to "{self.device.name}" has failed '
                                   f'after {retries} tries')

        return response

    @BaseConnection.locked
    @isconnected
    def delete(self, api_url, expected_status_code=requests.codes.ok,
               timeout=30, retries=3, retry_wait=10, content_type='json'):
        """DELETE REST Command to delete information from the device
        Arguments
        ---------

            api_url (string): subdirectory part of the API URL
            expected_status_code (int): Expected result
            timeout (int): Maximum time
        """
        if not self.connected:
            raise Exception(f"'{self.device.name}' is not connected for "
                            f"alias '{self.alias}'")
        # Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = f'{self.url}{api_url}'

        log.info(f"Sending DELETE command to '{self.device.name}':" \
                 f"\nURL: {full_url}")

        for i in range(retries):
            try:
                # Send to the device
                response = self.session.delete(full_url, timeout=timeout, verify=False)
                break
            except Exception:
                log.warning(f'Request to {self.device.name} failed. Waiting {retry_wait} seconds before retrying\n', exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException(f'Sending "{full_url}" to "{self.device.name}" has failed '
                                   f'after {retries} tries')

        try:
            # response might not pe in JSON format
            output = response.json()
            log.info(f"Output received:\n{output}")
        except ValueError:
            output = response.text
            log.info(f"'Delete' operation did not return a json response: {output}")

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException(f"DELETE {full_url} to {self.device.name} has returned the "
                                   f"following code '{response.status_code}', instead of the "
                                   f"expected status code '{expected_status_code}'"
                                   f", got:\n {response.text}")
        return output

    @BaseConnection.locked
    @isconnected
    def delete(self, api_url, params=None, data=None, json=None, files=None,
             timeout=30, retries=3, retry_wait=10) -> requests.Response:
        """POST REST Command to configure information from the device
        Arguments
        ---------
            api_url (string): subdirectory part of the API URL
            params (dict): Query string parameters
            data (dict):
            json (json) : if request header Content-Type is application/json
            files (dict):
            timeout (int): Maximum time
        """

        if not self.connected:
            raise Exception(f"'{self.device.name}' is not connected for "
                            f"alias '{self.alias}'")
        # Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = f'{self.url}{api_url}'

        for _ in range(retries):
            try:
                if params and not json:
                    response = self.session.delete(full_url, params=params, timeout=timeout,
                                                 verify=self.verify)
                elif params and json:
                    response = self.session.delete(full_url, params=params, json=json,
                                                 timeout=timeout, verify=self.verify)
                elif json and not params:
                    response = self.session.delete(full_url, json=json,
                                                 timeout=timeout, verify=self.verify)
                elif data:
                    response = self.session.delete(full_url, data=data,
                                                 timeout=timeout, verify=self.verify)
                elif files:
                    response = self.session.delete(full_url, files=files,
                                                 timeout=timeout, verify=self.verify)
                else:
                    response = self.session.delete(full_url, timeout=timeout, verify=self.verify)

                break
            except Exception:
                log.warning(f'Request to {self.device.name} failed. '
                            f'Waiting {retry_wait} seconds before retrying\n'
                            , exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException(f'Sending "{full_url}" to "{self.device.name}" has failed '
                                   f'after {retries} tries')

        return response

