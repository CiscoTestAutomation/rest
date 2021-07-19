
Robot framework
===============

Example script for robot framework.


.. code-block:: robotframework

    *** Settings ***
    Library   pyats.robot.pyATSRobot
    Library   rest.connector.RestRobot
    
    *** Test Cases ***
    Test REST
        use testbed "testbed.yaml"
        connect to device   device=R1  via=rest  alias=rest
        rest get   R1  /test
