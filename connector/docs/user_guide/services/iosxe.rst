IOS-XE
======

The following services are supported by the REST connector for IOS-XE.


connect
-------

API to connect to the device.

The IOS-XE REST implementation supports specifying the port to connect to 
and allows to specify the username and password in the testbed YAML file.

.. code-block:: yaml

    # Example
    # -------
    #
    #   pyATS testbed yaml example for defining a REST connection

    testbed:
        name: myTestbed

    devices:
        eWLC:
            custom:
                abstraction:
                    order: [os]
            os: iosxe
            type: router

            connections:
                rest:
                    # Rest connector class
                    class: rest.connector.Rest
                    ip: 1.2.3.4
                    port: 443
                    username: admin
                    password: admin


If no port is specified, he default of `443` is used.
If no username or password is specified, the default of `admin` is used.

When connecting to this device, an optional proxies argument may be specified.
If not specified, proxies are loaded from the environment if they have been
set.

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
    device.connect(via='rest', proxies={
            'http': 'http://proxy.domain.com:80/',
            'https': 'http://proxy.domain.com:80/',
            'ftp': 'http://proxy.domain.com:80/',
            'no': '.mydomain.com',
        }
    )

    # Get information
    device.rest.get(url)







.. csv-table:: GET arguments
    :header: Argument, Description, Default

    ``default_content_type``, "Default content type for GET requests, json or xml", json
    ``timeout``, Maximum time it can take to disconnect to the device. (optional), 30


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
    ``content_type``, Content type to be returned (xml or json) (optional), json
    ``headers``, Dictionary of headers (optional),
    ``expected_status_codes``, List of expected status codes (optional), 200
    ``timeout``, timeout in seconds (optional), 30

.. code-block:: python

    url = '/restconf/data/site-cfg-data/'
    output = device.rest.get(url)


post
----

API to send POST command with optional payload to the device.

.. csv-table:: POST arguments
    :header: Argument, Description, Default

    ``api_url``, API url string (required), 
    ``payload``, "payload to sent, can be string or dict (optional)",
    ``content_type``, content type to be returned (xml or json) (optional),
    ``headers``, dictionary of HTTP headers (optional),
    ``expected_status_codes``, list of expected result codes (optional), "200, 201, 204"
    ``timeout``, timeout in seconds (optional), 30
..

    If the content_type option is not passed, the script will try to detect 
    if the payload is XML, otherwise it will assume JSON.  The content-type and accept 
    headers will be set based on the detected payload or on the passed content-type. 

    If you pass a `dict()` object as payload, a conversion will be done to JSON or XML string.

.. code-block:: python

    url = '/restconf/data/site-cfg-data/ap-cfg-profiles/'
    output = device.rest.post(url)


patch
-----

API to send POST command with payload to the device.

.. csv-table:: PATCH arguments
    :header: Argument, Description, Default

    ``api_url``, API url string (required)
    ``payload``, "payload to sent, can be string or dict (required)"
    ``content_type``, content type to be returned (xml or json) (optional),
    ``headers``, dictionary of HTTP headers (optional)
    ``expected_status_codes``, list of expected result codes (optional), "200, 201, 204"
    ``timeout``, timeout in seconds (optional), 30
..

    If the content_type option is not passed, the script will try to detect 
    if the payload is XML, otherwise it will assume JSON.  The content-type and accept 
    headers will be set based on the detected payload or on the passed content-type. 

    If you pass a `dict()` object as payload, a conversion will be done to JSON or XML string.


.. code-block:: python

    hyperlocation_enable = """
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "hyperlocation": {
            "hyperlocation-enable": true,
        }
    }
    """
    output = device.rest.patch("/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile", payload=hyperlocation_enable)


put
---

API to send PUT command with payload to the device.

.. csv-table:: PUT arguments
    :header: Argument, Description, Default

    ``api_url``, API url string (required)
    ``payload``, "payload to sent, can be string or dict (required)"
    ``content_type``, content type to be returned (xml or json) (optional),
    ``headers``, dictionary of HTTP headers (optional)
    ``expected_status_codes``, list of expected result codes (optional), "200, 201, 204"
    ``timeout``, timeout in seconds (optional), 30
..

    If the content_type option is not passed, the script will try to detect 
    if the payload is XML, otherwise it will assume JSON.  The content-type and accept 
    headers will be set based on the detected payload or on the passed content-type. 

    If you pass a `dict()` object as payload, a conversion will be done to JSON or XML string.

.. code-block:: python

    hyperlocation_enable = """
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "hyperlocation": {
            "hyperlocation-enable": true,
        }
    }
    """
    output = device.rest.put("/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile", payload=hyperlocation_enable)


delete
------

API to send DELETE command with payload to the device.

.. csv-table:: DELETE arguments
    :header: Argument, Description, Default

    ``api_url``, API url string (required)
    ``content_type``, content type to be returned (xml or json),
    ``headers``, dictionary of HTTP headers (optional),
    ``expected_status_codes``, list of expected result codes, "200, 201, 204"
    ``timeout``, timeout in seconds (optional), 30

.. code-block:: python
    
   device.rest.delete('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=test-profile')


.. sectionauthor:: Maaz Mashood Mohiuddin <mmashood@cisco.com>

