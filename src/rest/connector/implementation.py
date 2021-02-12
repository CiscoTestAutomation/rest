from pyats.connections import BaseConnection


class Implementation(BaseConnection):
    '''Rest BaseClass

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
                        ip : "2.3.4.5"
                        port: "443"
                        protocol: https
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

        # instanciate BaseConnection
        # (could use super...)
        BaseConnection.__init__(self, *args, **kwargs)
        self._is_connected = False

    @property
    def connected(self):
        '''Is a device connected'''
        return self._is_connected

    def connect(self, *args, **kwargs):
        '''connect to the device via REST'''

        raise NotImplementedError

    def disconnect(self):
        '''disconnect the device for this particular alias'''

        raise NotImplementedError

    def get(self, *args, **kwargs):
        '''GET REST Command to retrieve information from the device'''

        raise NotImplementedError

    def post(self, *args, **kwargs):
        '''POST REST Command to configure information from the device'''

        raise NotImplementedError

    def put(self, *args, **kwargs):
        '''PUT REST Command to update information on the device'''

        raise NotImplementedError

    def patch(self, *args, **kwargs):
        '''PATCH REST Command to update information on the device'''

        raise NotImplementedError

    def delete(self, *args, **kwargs):
        '''DELETE REST Command to delete information from the device'''

        raise NotImplementedError

    def configure(self, *args, **kwargs):
        '''configure - Not implemented for REST'''
        raise NotImplementedError('configure is not a supported method for REST. '
                                  'post is probably what you are looking for')

    def execute(self, *args, **kwargs):
        '''execute - Not implemented for REST'''
        raise NotImplementedError('execute is not a supported method for REST. '
                                  'get is probably what you are looking for.')
