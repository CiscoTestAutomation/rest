"""rest.connector module defines a connection implementation to communicate to
the device via REST api"""

# metadata
__version__ = '1.0.1'
__author__ = 'Jean-Benoit Aubin <jeaubin@cisco.com>'
__contact__ = 'pyats-support@cisco.com'
__copyright__ = 'Cisco Systems, Inc. Cisco Confidential'


from ats.connections import BaseConnection

# For abstract
from abstract import Lookup
import rest.connector.libs

# create a logger for this module


class Rest(BaseConnection):
    '''Rest

    Used for picking the right abstraction of REST implementatin based on the
    device, via abstraction

    It also overwrittes __getattribute__ to go look in the right abstracted
    class
    '''

    def __init__(self, *args, **kwargs):
        '''__init__ instantiates a single connection instance.'''

        super().__init__(*args, **kwargs)

        # Set up abstraction for this device
        lookup = Lookup.from_device(self.device)
        _implementation = lookup.libs.implementation.Implementation
        self._implementation = _implementation(*args, **kwargs)

    def __getattribute__(self, name):
        '''Redirect specific name of function to the specific implementation'''

        # Selector of methods/attributes to pick from abstracted
        # Can't use __getattr__ as BaseConnection is abstract and some already
        # exists
        if name in ['get', 'post', 'connect', 'disconnect', 'delete',
                    'connected']:
            return getattr(self._implementation, name)

        # Send the rest to normal __getattribute__
        return super().__getattribute__(name)
