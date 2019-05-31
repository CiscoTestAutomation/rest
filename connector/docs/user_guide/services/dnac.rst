DNAC
====

The following services are supported by the REST connector for DNAC.


connect
-------

API to connect to the device.

The DNAC REST implementation supports specifying the port to connect to 
and allows to specify the username and password in the testbed YAML file.

.. code-block:: yaml

    # Example
    # -------
    #
    #   pyATS testbed yaml example for defining a REST connection

    testbed:
        name: myTestbed

    devices:
        dnac:
            custom:
                abstraction:
                    order: [os]
            connections:
                rest:
                    # Rest connector class
                    class: rest.connector.Rest
                    ip: 1.2.3.4
                    port: 8080
                    username: admin
                    password: admin
                    verify: False


If no port is specified, the default of `443` is used. If verify is provided
and is False, it wont verify the SSL certificate.

.. csv-table:: GET arguments
    :header: Argument, Description, Default

    ``timeout``, Maximum time it can take to connect to the device. (optional), 30


disconnect
----------

same as the `generic`_ implementation.

.. _generic: generic.html#disconnect


get
---

API to send GET command to the device.

.. csv-table:: GET arguments
    :header: Argument, Description, Default

    ``api_url``,  API url string (required),
    ``timeout``, timeout in seconds (optional), 30

.. code-block:: python

    url = '/dna/intent/api/v1/interface'
    output = device.rest.get(url)

.. sectionauthor:: Jean-Benoit Aubin <jeaubin@cisco.com>

