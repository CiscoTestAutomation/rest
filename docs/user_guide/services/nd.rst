ND
====

The following services are supported by the REST connector for ND.


get
---

API to send GET command to the device.

.. list-table:: GET arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - api_url
      - API url (subdirectory part of the url) string
      - Mandatory
    * - expected_status_code (int)
      - Expected result
      - None
    * - timeout
      - Maximum time it can take to disconnect to the device
      - 30 seconds

.. code-block:: python

    # Assuming the device is already connected
    url = '/api/config/class/localusers/'
    output = device.get(url)

post
----

API to send POST command to the device.

.. list-table:: POST arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - api_url
      - API url (subdirectory part of the url) string
      - Mandatory
    * - payload (dict)
      - Dictionary containing the information to send via the post
      - Mandatory
    * - expected_status_code (int)
      - Expected result
      - 200
    * - timeout (int)
      - Maximum time it can take to disconnect to the device
      - 30 seconds

.. code-block:: python

    # Assuming the device is already connected
    payload = """
    {
      "loginID": "test",
      "loginPasswd: "cisco!123"
    }
    """

    url = 'api/config/localusers/test'
    device.rest.post(url, payload)

delete
------

API to send DELETE command to the device.

.. list-table:: DELETE arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - api_url
      - API url (subdirectory part of the url) string
      - Mandatory
    * - expected_status_code (int)
      - Expected result
      - 200
    * - timeout (int)
      - Maximum time it can take to disconnect to the device
      - 30 seconds

.. code-block:: python

    # Assuming the device is already connected
    url = 'api/config/localusers/test'
    device.delete(url)


.. sectionauthor:: Romel Tolos <rtolos@cisco.com>
