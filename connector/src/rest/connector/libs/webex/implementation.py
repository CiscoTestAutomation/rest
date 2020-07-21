import json
import logging

import requests
from requests.exceptions import RequestException

from pyats.connections import BaseConnection
from pyats import configuration as cfg
from rest.connector.implementation import Implementation

# create a logger for this module
log = logging.getLogger(__name__)

MESSAGE_URL = 'https://api.ciscospark.com/v1/messages'

class Implementation(Implementation):
    '''Rest Implementation for WebEx Teams

    Implementation of Rest connection to WebEx Teams

    YAML Example
    ------------

        devices:
            webex:
                os: webex
                connections:
                    rest:
                        class: rest.connector.Rest
                        token: guieaguroeihjigroh
                        roomid: grjiaeoghrioeahgrioea
                custom:
                    abstraction:
                        order: [os]

    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('topology.yaml')
        >>> device = testbed.devices['webex']
        >>> device.connect(alias='rest', via='rest')
        >>> device.rest.connected
        True
    '''

    CUSTOM_APIS = ['notify']

    def __init__(self, *args, token=None, space=None, email=None, **kwargs):
        super().__init__(*args, **kwargs)
        token = token or cfg.get('webex.token')
        if not token:
            raise ConnectionError('No WebEx Token. Cannot make connector.')
        self.headers = {'Authorization': 'Bearer {}'.format(token),
                        'Content-Type': 'application/json'}

    @BaseConnection.locked
    def connect(self):
        self._is_connected = True

    @BaseConnection.locked
    def disconnect(self):
        self._is_connected = False

    @BaseConnection.locked
    def notify(self, msg, space=None, email=None, verbose=False):
        '''POST message to WebEx Teams

        Arguments
        ---------
        msg: Markdown message to send to WebEx Teams
        space: ID of WebEx space to post to
        email: Email of individual to send notification to
        verbose: enable verbose logging
        '''
        space = space or cfg.get('webex.space')
        email = email or cfg.get('webex.email')

        # Form payload, send to a space if provided, else a person if provided
        payload = {'markdown': msg}
        if space:
            payload['roomId'] = space
        elif email:
            payload['toPersonEmail'] = email
        else:
            raise TypeError('notify requires a space or an email to be '
                            'provided')

        log.debug('Sending POST to {u}'.format(u=MESSAGE_URL))
        log.debug("Request headers: {h}\nPayload: {p}"
                .format(h=self.headers, p=json.dumps(payload)))

        r = requests.post(MESSAGE_URL,
                          data=json.dumps(payload),
                          headers=self.headers)

        log.debug("Response: {c} {r}, headers: {h}"
                  .format(c=r.status_code, r=r.reason, h=r.headers))
        if verbose:
            log.info('Output received: %s' % r.text)

        expected_codes = [requests.codes.created,
                          requests.codes.no_content,
                          requests.codes.ok]

        if not r.status_code in expected_codes:
            # Something went wrong with the request
            raise RequestException("'{c}' result code has been returned "
                                   "instead of the expected status code(s) "
                                   "'{e}' for '{d}'\n{t}"
                                   .format(d=self.device.name,
                                           c=r.status_code,
                                           e=expected_codes,
                                           t=r.text))

        return r
