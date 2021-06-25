from functools import wraps
from importlib import import_module
from logging import getLogger
from pprint import pformat
from re import search
import urllib3

from pyats.connections import BaseConnection
from rest.connector.utils import get_username_password, verify_apic_version

# create a logger for this module
log = getLogger(__name__)


class AciCobra(BaseConnection):
    """ACI SDK (Cobra) Implementation for APIC

    Implementation of ACI SDK connection to devices
    based on pyATS BaseConnection for APIC

    YAML Example
    ------------

        devices:
            apic1:
                connections:
                    cobra:
                        class: rest.connector.Acisdk
                        ip : "2.3.4.5"
                credentials:
                    cobra:
                        username: admin
                        password: cisco123

    Code Example
    ------------

        >>> from pyats.topology import loader
        >>> testbed = loader.load('/users/xxx/xxx/testbed.yaml')
        >>> device = testbed.devices['apic1']
        >>> device.connect(alias='cobra', via='cobra')
        >>> device.rest.connected
        True
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mo_dir = None

        # remove warnings for insecure HTTPS
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self._is_connected = False

        if 'host' in self.connection_info:
            ip = self.connection_info['host']
        else:
            ip = self.connection_info['ip'].exploded
        if 'port' in self.connection_info:
            port = self.connection_info['port']
            self.url = f'https://{ip}:{port}/'
        else:
            self.url = f'https://{ip}/'

        verify_apic_version(ip)

    @property
    def connected(self):
        """Is a device connected"""
        return self._is_connected

    @BaseConnection.locked
    def connect(self, timeout=90):
        """
        Connect to the device via ACI SDK
        Arguments
        ---------
            timeout (int): Timeout value
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
                apic1:
                    connections:
                        cobra:
                            class: rest.connector.Acisdk
                            ip : "2.3.4.5"
                    credentials:
                        cobra:
                            username: admin
                            password: cisco123
        Code Example
        ------------
            >>> from pyats.topology import loader
            >>> testbed = loader.load('/users/xxx/xxx/testbed.yaml')
            >>> device = testbed.devices['apic1']
            >>> device.connect(alias='cobra', via='cobra')
        """

        if self.connected:
            return

        username, password = get_username_password(self)

        LoginSession = getattr(import_module('cobra.mit.session'), 'LoginSession')
        session = LoginSession(self.url, username, password, timeout=timeout)

        MoDirectory = getattr(import_module('cobra.mit.access'), 'MoDirectory')
        self.mo_dir = MoDirectory(session)

        log.info("Connecting to '{d}' with alias "
                 "'{a}'".format(d=self.device.name, a=self.alias))

        self.mo_dir.login()

        self._is_connected = True
        log.info("Connected successfully to '{d}'".format(d=self.device.name))

    def disconnect(self):
        """disconnect the device for this particular alias"""

        log.info("Disconnecting from '{d}' with "
                 "alias '{a}'".format(d=self.device.name, a=self.alias))
        try:
            self.mo_dir.logout()
        finally:
            self._is_connected = False
        log.info("Disconnected successfully from "
                 "'{d}'".format(d=self.device.name))

    def is_connected(func):
        """Decorator to make sure session to device is active
           There is limitation on the amount of time the session cab be active
           on the APIC. However, there are no way to verify if
           session is still active unless sending a command. So, its just
           faster to reconnect every time.
        """
        @wraps(func)
        def decorated(self, *args, **kwargs):
            # Check if connected
            try:
                ret = func(self, *args, **kwargs)
            except Exception as e:
                if not hasattr(e, 'reason') or e.reason != 'Token was invalid (Error: Token timeout)':
                    raise

                self.disconnect()

                if 'timeout' in kwargs:
                    self.connect(timeout=kwargs['timeout'])
                else:
                    self.connect()

                ret = func(self, *args, **kwargs)
            return ret

        return decorated

    def log_action(func):
        """Decorator to log the actions made by MoDirectory functions.
        """
        @wraps(func)
        def decorated(self, *args, **kwargs):

            ret = func(self, *args, **kwargs)
            log.info(f'Output of function {func.__name__} is:\n{pformat(ret, indent=2)}')
            return ret

        return decorated

    @BaseConnection.locked
    @is_connected
    @log_action
    def query(self, queryObject):
        """
        Queries the MIT for a specified object. The queryObject provides a
        variety of search options.
        """
        return self.mo_dir.query(queryObject)

    @BaseConnection.locked
    @is_connected
    @log_action
    def commit(self, configObject, sync_wait_timeout=None):
        """
        Short-form commit operation for a configRequest
        """
        return self.mo_dir.commit(configObject, sync_wait_timeout=sync_wait_timeout)

    @BaseConnection.locked
    @is_connected
    @log_action
    def lookupByDn(self, dnStrOrDn, **queryParams):
        """
        A short-form managed object (MO) query using the distinguished name(Dn)
        of the MO.

        Args:
          dnStrOrDn:   dn of the object to lookup
          queryParams: a dictionary including the properties to the
            added to the query.
        """
        return self.mo_dir.lookupByDn(dnStrOrDn, **queryParams)

    @BaseConnection.locked
    @is_connected
    @log_action
    def lookupByClass(self, classNames, parentDn=None, **queryParams):
        """
        A short-form managed object (MO) query by class.

        Args:
          classNames: Name of the class to lookup
          parentDn:   dn of the root object were to start search from (optional)
          queryParams: a dictionary including the properties to the
            added to the query.
        """
        return self.mo_dir.lookupByClass(classNames, parentDn=parentDn, **queryParams)

    @BaseConnection.locked
    @is_connected
    @log_action
    def exists(self, dnStrOrDn):
        """Checks if managed object (MO) with given distinguished name (dn) is present or not

        Args:
          dnStrOrDn (str or cobra.mit.naming.Dn): A distinguished name as a
            :class:`cobra.mit.naming.Dn` or string

        Returns:
          bool: True, if MO is present, else False.
        """
        return self.mo_dir.exists(dnStrOrDn)

    @BaseConnection.locked
    @is_connected
    @log_action
    def getModel(self, model):
        """
        Automatically imports the required library and returns the model
        :param model: must contain module and class of desired model (eg. fv.Tenant)
        :return: requested Cobra model
        """
        module = None
        attribute = None

        if '.' in model:
            module, attribute = model.rsplit('.', 1)
        else:
            match = search(r'([a-z]*)([A-Z]\w*)', model)
            if match:
                module, attribute = match.groups()

        if module and attribute:
            return getattr(import_module(f'cobra.model.{module}'), attribute)
        else:
            raise NameError("'model' must contain <module>.<class of object>")

    def create(self, model, parentMoOrDn, **extra_parms):
        return self.getModel(model)(parentMoOrDn, **extra_parms)

    @BaseConnection.locked
    @is_connected
    @log_action
    def configAndCommit(self, mo, sync_wait_timeout=None):
        """
        Add MO to ConfigRequest and push it to device
        :param mo:
        :return:
        """
        config = getattr(import_module(f'cobra.mit.request'), 'ConfigRequest')()
        config.addMo(mo)
        resp = self.mo_dir.commit(configObject=config, sync_wait_timeout=sync_wait_timeout)
        if resp.status_code == 200:
            return 'Ok'
        else:
            return (f'Commit failed with code {resp.status_code}\n'
                    f'and message {resp.text}')
