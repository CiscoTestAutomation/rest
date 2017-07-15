Generic
=======

The following generic services are supported by all implementations.


connect
-------

API to connect to the device.

.. csv-table:: connect arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"

.. code-block:: python

    # Example
    # -------
    #
    #   loading & using REST testbed yaml file in pyATS

    # import the topology module
    from ats import topology

    # load the above testbed file containing REST device
    testbed = topology.loader.load('/path/to/rest/testbed.yaml')

    # get device by name
    device = testbed.devices['PE1']

    # connect to it 
    device.connect(via='rest')

disconnect
----------

API to disconnect from the device.

.. csv-table:: disconnect arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"

.. code-block:: python

    # Example
    # -------
    #
    #   loading & using REST testbed yaml file in pyATS

    # import the topology module
    from ats import topology

    # load the above testbed file containing REST device
    testbed = topology.loader.load('/path/to/rest/testbed.yaml')

    # get device by name
    device = testbed.devices['PE1']

    # connect to it 
    device.connect(via='rest')

    # disconnect rest connection 
    device.rest.disconnect()

