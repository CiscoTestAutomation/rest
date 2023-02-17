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
                        password: cisco123

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
    def connect(self, timeout=30, retries=3, retry_wait=10):
        """connect to the device via REST
        Arguments
        ---------
            timeout (int): Timeout value
            retries (int): Max retries on request exception (default: 3)
            retry_wait (int): Seconds to wait before retry (default: 10)

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
                            password: cisco123

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
            self.url = 'https://{ip}:{port}/'.format(ip=ip, port=port)
        else:
            self.url = 'https://{ip}/'.format(ip=ip)
        login_url = '{f}login'.format(f=self.url)

        username, password = get_username_password(self)

        payload = {
            "userName": username,
            "userPasswd": password,
            "domain": "DefaultAuth"
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
                    raise RequestException("Connection to '{ip}' has returned the "
                                           "following code '{c}', instead of the "
                                           "expected status code '{ok}'"
                                           .format(ip=ip, c=response.status_code,
                                                   ok=requests.codes.ok))
                break
            except Exception:
                log.warning('Request to {} failed. Waiting {} seconds before retrying\n'.format(
                    self.device.name, retry_wait), exc_info=True)
                time.sleep(retry_wait)
        else:
            raise ConnectionError('Connection to {} failed'.format(self.device.name))

        self._is_connected = True
        log.info("Connected successfully to '{d}'".format(d=self.device.name))

    @BaseConnection.locked
    def disconnect(self):
        """disconnect the device for this particular alias"""

        log.info("Disconnecting from '{d}' with "
                 "alias '{a}'".format(d=self.device.name, a=self.alias))
        try:
            self.session.close()
        finally:
            self._is_connected = False
        log.info("Disconnected successfully from "
                 "'{d}'".format(d=self.device.name))

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
            timeout=30, retries=3, retry_wait=10):
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
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))
        #Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = "{f}{api_url}".format(f=self.url, api_url=api_url)

        log.info("Sending GET command to '{d}':" \
                 "\nURL: {furl}".format(d=self.device.name, furl=full_url))

        for _ in range(retries):
            try:
                response = self.session.get(full_url, timeout=timeout, verify=False)
                break
            except Exception:
                log.warning('Request to {} failed. Waiting {} seconds before retrying\n'.format(
                    self.device.name, retry_wait), exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException('Sending "{furl}" to "{d}" has failed '
                                   'after {tries} tries'.format(furl=full_url,
                                                                d=self.device.name,
                                                                tries=retries))

        try:
            output = response.json()
        except Exception:
            output = response.text

        log.info("Output received:\n{output}".format(output=
            json.dumps(output, indent=2, sort_keys=True)))

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException("GET {furl} to {d} has returned the "
                                   "following code '{c}', instead of the "
                                   "expected status code '{e}'"
                                   ", got:\n {msg}".format(furl=full_url,
                                                  d=self.device.name,
                                                  c=response.status_code,
                                                  e=expected_status_code,
                                                  msg=response.text))
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
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))
        # Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = '{f}{api_url}'.format(f=self.url, api_url=api_url)

        log.info("Sending POST command to '{d}':" \
                 "\nURL: {furl}\nPayload:{p}".format(d=self.device.name,
                                                     furl=full_url,
                                                     p=payload))
        headers = {'form': 'application/x-www-form-urlencoded',
                   'json': 'application/json',
                   'xml': 'application/xml'}

        if content_type == 'form' and isinstance(payload, dict):
            payload = urllib.parse.urlencode(payload, safe=':!')
        elif content_type == 'xml':
            if isinstance(payload, dict):
                raise ValueError("Error on {d} during POST command: "
                                 "Payload needs to be string in xml format if used "
                                 "in conjunction with content_type='xml' argument"
                                 .format(d=self.device.name))

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
                log.warning('Request to {} failed. Waiting {} seconds before retrying\n'.format(
                    self.device.name, retry_wait), exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException('Sending "{furl}" to "{d}" has failed '
                                   'after {tries} tries'.format(furl=full_url,
                                                                d=self.device.name,
                                                                tries=retries))

        try:
            # response might not pe in JSON format
            output = response.json()
            log.info("Output received:\n{output}".format(output=output))
        except Exception:
            output = response.content if content_type == 'xml' else response.text
            log.info(f"'Post' operation did not return a json response: {output}")

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException("POST {furl} to {d} has returned the "
                                   "following code '{c}', instead of the "
                                   "expected status code '{e}'"
                                   ", got:\n {msg}".format(furl=full_url,
                                                  d=self.device.name,
                                                  c=response.status_code,
                                                  e=expected_status_code,
                                                  msg=response.text))
        return output

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
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))
        # Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = '{f}{api_url}'.format(f=self.url, api_url=api_url)

        log.info("Sending PUT command to '{d}':" \
                 "\nURL: {furl}\nPayload:{p}".format(d=self.device.name,
                                                     furl=full_url,
                                                     p=payload))
        headers = {'form': 'application/x-www-form-urlencoded',
                   'json': 'application/json',
                   'xml': 'application/xml'}

        if content_type == 'form' and isinstance(payload, dict):
            payload = urllib.parse.urlencode(payload, safe=':!')
        elif content_type == 'xml':
            if isinstance(payload, dict):
                raise ValueError("Error on {d} during PUT command: "
                                 "Payload must to be string in xml format if used "
                                 "in conjunction with content_type='xml' argument"
                                 .format(d=self.device.name))

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
                log.warning('Request to {} failed. Waiting {} seconds before retrying\n'.format(
                    self.device.name, retry_wait), exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException('Sending "{furl}" to "{d}" has failed '
                                   'after {tries} tries'.format(furl=full_url,
                                                                d=self.device.name,
                                                                tries=retries))

        try:
            # response might not pe in JSON format
            output = response.json()
            log.info("Output received:\n{output}".format(output=output))
        except Exception:
            output = response.content if content_type == 'xml' else response.text
            log.info(f"'Put' operation did not return a json response: {output}")

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException("PUT {furl} to {d} has returned the "
                                   "following code '{c}', instead of the "
                                   "expected status code '{e}'"
                                   ", got:\n {msg}".format(furl=full_url,
                                                  d=self.device.name,
                                                  c=response.status_code,
                                                  e=expected_status_code,
                                                  msg=response.text))
        return output

    @BaseConnection.locked
    @isconnected
    def delete(self, api_url, expected_status_code=requests.codes.ok,
               timeout=30, retries=3, retry_wait=10):
        """DELETE REST Command to delete information from the device
        Arguments
        ---------

            api_url (string): subdirectory part of the API URL
            expected_status_code (int): Expected result
            timeout (int): Maximum time
        """
        if not self.connected:
            raise Exception("'{d}' is not connected for "
                            "alias '{a}'".format(d=self.device.name,
                                                 a=self.alias))
        # Eliminate the starting "/" if present, as it may cause problems
        api_url = api_url.lstrip('/')
        # Deal with the url
        full_url = '{f}{api_url}'.format(f=self.url, api_url=api_url)

        log.info("Sending DELETE command to '{d}':" \
                 "\nURL: {furl}".format(d=self.device.name, furl=full_url))

        for i in range(retries):
            try:
                # Send to the device
                response = self.session.delete(full_url, timeout=timeout, verify=False)
                break
            except Exception:
                log.warning('Request to {} failed. Waiting {} seconds before retrying\n'.format(
                    self.device.name, retry_wait), exc_info=True)
                time.sleep(retry_wait)
        else:
            raise RequestException('Sending "{furl}" to "{d}" has failed '
                                   'after {tries} tries'.format(furl=full_url,
                                                                d=self.device.name,
                                                                tries=retries))

        try:
            # response might not pe in JSON format
            output = response.json()
            log.info("Output received:\n{output}".format(output=output))
        except ValueError:
            output = response.text
            log.info(f"'Delete' operation did not return a json response: {output}")

        # Make sure it returned requests.codes.ok
        if response.status_code != expected_status_code:
            # Something bad happened
            raise RequestException("DELETE {furl} to {d} has returned the "
                                   "following code '{c}', instead of the "
                                   "expected status code '{e}'"
                                   ", got:\n {msg}".format(furl=full_url,
                                                  d=self.device.name,
                                                  c=response.status_code,
                                                  e=expected_status_code,
                                                  msg=response.text))
        return output
