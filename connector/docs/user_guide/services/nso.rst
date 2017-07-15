NSO
===

The following services are supported by the REST connector for NSO.


get
---

API to send GET command to the device.

.. csv-table:: GET arguments
    :header: Argument, Description, Default

    ``api_url``,  API url string (required),
    ``content_type``, Content type to be returned (xml or json) (optional), JSON
    ``headers``, Dictionary of headers (optional),
    ``expected_status_codes``, List of expected status codes (optional), 200
    ``timeout``, Maximum time it can take to disconnect to the device. (optional), 30

.. code-block:: python

    url = '/api/running/devices'
    output = device.rest.get(url)


post
----

API to send POST command with optional payload to the device.

.. csv-table:: POST arguments
    :header: Argument, Description, Default

    ``api_url``, API url string (required), 
    ``payload``, "payload to sent, can be string or dict (optional)",
    ``content_type``, content type to be returned (xml or json) (optional), JSON
    ``headers``, dictionary of HTTP headers (optional),
    ``expected_status_codes``, list of expected result codes (optional), "200, 201, 204"
    ``timeout``, timeout in seconds (optional), 30
..

    If the content_type option is not passed, the script will try to detect 
    if the payload is XML, otherwise it will assume JSON.  The content-type and accept 
    headers will be set based on the detected payload or on the passed content-type. 

    If you pass a `dict()` object as payload, a conversion will be done to JSON or XML string.

.. code-block:: python

    url = '/api/running/devices/device/R1/_operations/check-sync
    output = device.rest.post(url)


patch
-----

API to send POST command with payload to the device.

.. csv-table:: PATCH arguments
    :header: Argument, Description, Default

    ``api_url``, API url string (required)
    ``payload``, "payload to sent, can be string or dict (required)"
    ``content_type``, content type to be returned (xml or json) (optional), JSON
    ``headers``, dictionary of HTTP headers (optional)
    ``expected_status_codes``, list of expected result codes (optional), "200, 201, 204"
    ``timeout``, timeout in seconds (optional), 30
..

    If the content_type option is not passed, the script will try to detect 
    if the payload is XML, otherwise it will assume JSON.  The content-type and accept 
    headers will be set based on the detected payload or on the passed content-type. 

    If you pass a `dict()` object as payload, a conversion will be done to JSON or XML string.


.. code-block:: python

    config_routes = """
    {
      "tailf-ned-cisco-ios:route": {
        "ip-route-forwarding-list": [
          {
            "prefix": "10.6.1.0",
            "mask": "255.255.255.0",
            "forwarding-address": "10.2.2.2"
          }
        ]
      }
    }
    """
    output = device.rest.patch("/api/running/devices/device/R1/config/ios:ip/route", payload=config_routes)


put
---

API to send PUT command with payload to the device.

.. csv-table:: PUT arguments
    :header: Argument, Description, Default

    ``api_url``, API url string (required)
    ``payload``, "payload to sent, can be string or dict (required)"
    ``content_type``, content type to be returned (xml or json) (optional), JSON
    ``headers``, dictionary of HTTP headers (optional)
    ``expected_status_codes``, list of expected result codes (optional), "200, 201, 204"
    ``timeout``, timeout in seconds (optional), 30
..

    If the content_type option is not passed, the script will try to detect 
    if the payload is XML, otherwise it will assume JSON.  The content-type and accept 
    headers will be set based on the detected payload or on the passed content-type. 

    If you pass a `dict()` object as payload, a conversion will be done to JSON or XML string.

.. code-block:: python

    config_routes = """
    {
      "tailf-ned-cisco-ios:route": {
        "ip-route-forwarding-list": [
          {
            "prefix": "10.1.1.0",
            "mask": "255.255.255.0",
            "forwarding-address": "10.2.2.2"
          },
          {
            "prefix": "10.2.1.0",
            "mask": "255.255.255.0",
            "forwarding-address": "10.2.2.2"
          }
        ]
      }
    }
    """

    output = device.rest.put("/api/running/devices/device/R1/config/ios:ip/route", payload=config_routes)


delete
------

API to send DELETE command with payload to the device.

.. csv-table:: DELETE arguments
    :header: Argument, Description, Default

    ``api_url``, API url string (required)
    ``content_type``, content type to be returned (xml or json), JSON
    ``headers``, dictionary of HTTP headers (optional),
    ``expected_status_codes``, list of expected result codes, "200, 201, 204"
    ``timeout``, timeout in seconds (optional), 30

.. code-block:: python
    
   device.rest.delete('/api/running/devices/device/R1/config/ios:ip/route')


.. sectionauthor:: Dave Wapstra <dwapstra@cisco.com>

