"""rest.connector module defines a connection implementation to communicate to
the device via REST api"""

# metadata
__version__ = '24.4'
__author__ = ['Jean-Benoit Aubin <jeaubin@cisco.com>',
              'Takashi Higashimura (tahigash) <tahigash@cisco.com>']

__contact__ = 'pyats-support@cisco.com'
__copyright__ = 'Cisco Systems, Inc. Cisco Confidential'


from pyats.connections import BaseConnection

# For abstract
from genie.abstract import Lookup
import rest.connector.libs

# Ease of use (rest.connector.Acisdk)
from rest.connector.libs.apic.acisdk_implementation import AciCobra


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

        # Get the device platform, must be grabbed from the device dict as
        # platform can be populated from type if platform is not defined.
        # device_platform = self.device._to_dict().get('platform')
        if hasattr(self.device, 'platform') and self.device.platform:
            abstraction_tokens = ['os', 'platform']
        else:
            abstraction_tokens = ['os']

        # Set up abstraction for this device
        lookup = Lookup.from_device(self.device, default_tokens=abstraction_tokens)
        _implementation = lookup.libs.implementation.Implementation
        self._implementation = _implementation(*args, **kwargs)

    def __getattribute__(self, name):
        '''Redirect specific name of function to the specific implementation'''

        # Selector of methods/attributes to pick from abstracted
        # Can't use __getattr__ as BaseConnection is abstract and some already
        # exists
        if name in ['get', 'post', 'put', 'patch', 'delete',
                    'connect', 'disconnect', 'connected']:
            return getattr(self._implementation, name)

        # Send the rest to normal __getattribute__
        return super().__getattribute__(name)


class Acisdk(AciCobra):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
