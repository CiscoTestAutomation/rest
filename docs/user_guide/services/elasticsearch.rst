Elasticsearch
=============

The following services are supported by the REST connector for Elasticsearch.


get
---

API to send GET command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``headers``, "Headers to send with the GET command", "{Authorization: Bearer <access token>}"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    url = '/index_name/_search'
    output = device.rest.get(url)

post
----

API to send POST command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``payload``, "Payload to send to the device", "Mandatory"
    ``headers``, "Headers to send with the GET command", "{Authorization: Bearer <access token>}"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    payload = """
    {
      "banana": 100,
      "apple": 200
    }
    """

    url = 'index_store'
    device.rest.post(url, payload)

delete
------

API to send DELETE command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``headers``, "Headers to send with the GET command", "{Authorization: Bearer <access token>}"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    url = 'index_store/doc_id'
    device.rest.delete(url)

put
---

API to send PUT command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``payload``, "Payload to send to the device", "Mandatory"
    ``headers``, "Headers to send with the GET command", "{Authorization: Bearer <access token>}"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    payload = """
    {
      "banana": 100,
      "apple": 200
    }
    """

    url = 'index_store'
    output = device.rest.put(url, payload)

.. sectionauthor:: Takashi Higashimura <tahigash@cisco.com>

