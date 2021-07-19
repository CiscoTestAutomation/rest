import logging

from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

log = logging.getLogger(__name__)


class RestRobot(object):
    '''rest.connector RobotFramework library'''

    # Need to maintain the testscript object
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def __init__(self):
        # save builtin so we dont have to re-create then everytime
        self.builtin = BuiltIn()

        try:
            self.ats_pyats = self.builtin.get_library_instance('pyats.robot.pyATSRobot')
        except RobotNotRunningError:
            # return early during libdoc generation
            return
        except RuntimeError:
            try:
                self.ats_pyats = self.builtin.get_library_instance('ats.robot.pyATSRobot')
            except RuntimeError:
                # No pyATS
                raise RuntimeError(
                    "Missing mandatory 'Library  pyats.robot.pyATSRobot' in the Setting section")

    @property
    def testbed(self):
        return self.ats_pyats.testbed

    @keyword('rest get')
    def rest_get(self, device, *args, **kwargs):
        '''
        '''
        return self.testbed.devices[device].rest.get(*args, **kwargs)

    @keyword('rest patch')
    def rest_patch(self, device, *args, **kwargs):
        '''
        '''
        return self.testbed.devices[device].rest.patch(*args, **kwargs)

    @keyword('rest put')
    def rest_put(self, device, *args, **kwargs):
        '''
        '''
        return self.testbed.devices[device].rest.put(*args, **kwargs)

    @keyword('rest post')
    def rest_post(self, device, *args, **kwargs):
        '''
        '''
        return self.testbed.devices[device].rest.post(*args, **kwargs)

    @keyword('rest delete')
    def rest_delete(self, device, *args, **kwargs):
        '''
        '''
        return self.testbed.devices[device].rest.delete(*args, **kwargs)
