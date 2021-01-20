VIRL
====

The following services are supported by the REST connector for VIRL.


get
---

API to send GET command to the device.

.. csv-table:: GET arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``url``, "REST API url", "Mandatory"
    ``expected_status_code``, "Expected result", "200"

.. code-block:: python

    # Assuming the device is already connected
    url = '/simengine/rest/list'
    output = device.get(url)

post
----

API to send POST command to the device.

.. csv-table:: POST arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``url``, "REST API url", "Mandatory"
    ``payload``, "JSON data of VIRL config", "Mandatory"
    ``expected_status_code``, "Expected result", "200"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"

.. code-block:: python

    # Assuming the device is already connected
    payload = """
    {
        (VIRL Config)
    }
    """

    url = '/simengine/rest/launch'
    device.post(url, payload)

delete
------

API to send DELETE command to the device.

.. csv-table:: DELETE arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``url``, "REST API url", "Mandatory"
    ``expected_status_code``, "Expected result", "200"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"

.. code-block:: python

    # Assuming the device is already connected
    url = '/simengine/rest/tracking/{tracking_id}'
    output = device.delete(url)


.. sectionauthor:: Takashi Higashimura <tahigash@cisco.com>
