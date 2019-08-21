
Introduction
============

``Rest`` is a pyATS connection class implementation that allows scripts to
connect to a device using REST via topology/YAML format.

The ``rest.connector`` module is abstraction enabled and currently supports 
only specific platforms. Please note that the custom abstraction keyword is
required in the testbed.yaml file.


Supported platforms
-------------------


At the moment `rest.connector` supports the following platforms:

.. csv-table:: Rest connector supported platforms
    :header: "OS", "OWNER", "CONTACT"

    ``nxos``, Jean-Benoit Aubin, pyats-support-ext@cisco.com
    ``dnac``, Jean-Benoit Aubin, pyats-support-ext@cisco.com
    ``nso``, Dave Wapstra, dwapstra@cisco.com
    ``iosxe``, Maaz Mashood Mohiuddin, mmashood@cisco.com
    ``apic``, Takashi Higashimura, pyats-support-ext@cisco.com
    ``virl``, Takashi Higashimura, pyats-support-ext@cisco.com



Example use
-----------


To specify a ``Rest`` connection for your device, add the ``rest.connector.Rest`` class
to the connection for your devices in the testbed YAML file:

.. code-block:: yaml

    # Example
    # -------
    #
    #   pyATS testbed yaml example for defining a REST connection

    testbed:
        name: myTestbed

    devices:
        PE1:
            os: # This must be set to select the rest connector plugin to use.
                # The following values are supported :
                # nso, nxos, dnac, apic, iosxe
            type: router
            custom:
                abstraction:
                    order: [os]
            connections:
                # Console
                a:
                    ip: 1.2.3.4
                    port: 10001
                    protocol: telnet
                rest:
                    # specify the rest connector class
                    class: rest.connector.Rest
                    ip: 1.2.3.4
                    credentials:
                        rest:
                            username: my_username
                            password: my_password


With the above, the testbed loader can then load this YAML into object form.
After connecting using the ``rest`` connection, you can execute REST API services.
Please refer to the `services`_ section for details on supported services.

.. _services: services/index.html


.. code-block:: python

    # Example
    # -------
    #
    #   loading & using REST testbed yaml file in pyATS

    # import the topology module
    from pyats import topology

    # load the above testbed file containing REST device
    testbed = topology.loader.load('/path/to/rest/testbed.yaml')

    # get device by name
    device = testbed.devices['PE1']

    # connect to it 
    device.connect(via='rest')

    # get information of a particular DN
    url = '/api/mo/sys/bgp/inst/dom-default/af-ipv4-mvpn.json'
    output = device.rest.get(url)

