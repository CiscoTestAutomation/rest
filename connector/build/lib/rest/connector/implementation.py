from ats.connections import BaseConnection


class Implementation(BaseConnection):
    '''Rest BaseClass

    Baseclass for Rest connection implementation

    YAML Example
    ------------

        devices:
            PE1:
                tacacs:
                    login_prompt: "login:"
                    password_prompt: "Password:"
                    username: "admin"
                passwords:
                    tacacs: cisco123
                    enable: cisco123
                    line: cisco123
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
                        username: admin
                        password: cisco123

    Example
    -------

        >>> from ats.topology import loader
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
        '''connect to the device via REST

        Arguments
        ---------

            timeout (int): Timeout value

        Raises
        ------

        Exception
            If the connection did not go well

        Note
        ----

        There is no return from this method. If something goes wrong, an
        exception will be raised.


        YAML Example
        ------------

            devices:
                PE1:
                    tacacs:
                        login_prompt: "login:"
                        password_prompt: "Password:"
                        username: "admin"
                    passwords:
                        tacacs: admin
                        enable: admin
                        line: admin
                    connections:
                        a:
                            protocol: telnet
                            ip: "1.2.3.4"
                            port: 2004
                        vty:
                            protocol : telnet
                            ip : "2.3.4.5"
                        netconf:
                            class: rest.connector.Rest
                            ip : "2.3.4.5"

        Code Example
        ------------

            >>> from ats.topology import loader
            >>> testbed = loader.load('/users/xxx/xxx/asr22.yaml')
            >>> device = testbed.devices['asr22']
            >>> device.connect(alias='rest', via='rest')
        '''

        raise NotImplementedError


    def disconnect(self):
        '''disconnect the device for this particular alias'''

        raise NotImplementedError

    def get(self, *args, **kwargs):
        '''GET REST Command to retrieve information from the device

        Arguments
        ---------

            dn (string): Unique distinguished name that describes the object
                         and its place in the tree.
            rsp_subtree (string): Specifies child object level included in
                                  the response
            rsp_foreign_subtree (string):
            batch_size (int): Size of output to receive per batch
            batch_id (int): # in the sequence of the batch to receive
            expected_status_code (int): Expected result
        '''

        raise NotImplementedError

    def post(self, *args, **kwargs):
        '''POST REST Command to configure information from the device

        Arguments
        ---------

            dn (string): Unique distinguished name that describes the object
                         and its place in the tree.
            payload (dict): Dictionary containing the information to send via
                            the post
            expected_status_code (int): Expected result
            timeout (int): Maximum time
        '''

        raise NotImplementedError

    def delete(self, *args, **kwargs):
        '''DELETE REST Command to delete information from the device

        Arguments
        ---------

            dn (string): Unique distinguished name that describes the object
                         and its place in the tree.
            expected_status_code (int): Expected result
            timeout (int): Maximum time
        '''

        raise NotImplementedError


    def configure(self, *args, **kwargs):
        '''configure - Not implemented for REST'''
        raise NotImplementedError('execute is not a supported method for REST. '
                                  'post is probably what you are looking for')

    def execute(self, *args, **kwargs):
        '''execute - Not implemented for REST'''
        raise NotImplementedError('execute is not a supported method for REST. '
                                  'get is probably what you are looking for.')
